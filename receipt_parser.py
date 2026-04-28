"""
TR: PROJE: Market Fişi Veri Ayıklama Sistemi (Parsing) - Yeni Nesil API
    AÇIKLAMA: PaddleOCR predict() çıktısındaki (dt_polys, rec_texts) yapısını kullanarak
              satırları birleştiren ve verileri ayıklayan sınıf.
EN: PROJECT: Grocery Receipt Data Extraction System (Parsing) - Next-Gen API
    DESCRIPTION: A class that merges lines and extracts data using the (dt_polys, rec_texts) 
                 structure from PaddleOCR predict() output.
"""

import re

class ReceiptParser:
    def __init__(self, y_threshold=15):
        # Y-ekseni esik degeri (Ayni satirda sayilma toleransi)
        self.y_threshold = y_threshold

    def parse(self, prediction_result):
        """
        TR: PaddleOCR predict() çıktısını (liste içinde sözlük) alır.
        EN: Takes the PaddleOCR predict() output (dictionary inside a list).
        """
        if not prediction_result:
            return {'store_name': '', 'date': '', 'total_amount': 0.0, 'raw_lines': []}

        # Ilk resmin sonucunu al (tek resim isliyoruz)
        result = prediction_result[0]
        
        # 1. ADIM: Satirlari Birlestir
        merged_lines = self._merge_lines_from_predict(result)
        
        # 2. ADIM: Veri Ayiklama
        store_name = self._extract_store_name(merged_lines)
        date = self._extract_date(merged_lines)
        total_amount = self._extract_total_amount(merged_lines)

        return {
            'store_name': store_name,
            'date': date,
            'total_amount': total_amount,
            'raw_lines': merged_lines
        }

    def _merge_lines_from_predict(self, res):
        """
        predict() sonucundaki dt_polys ve rec_texts listelerini kullanarak 
        metinleri satirlara dizer.
        """
        if "dt_polys" not in res or "rec_texts" not in res:
            return []

        polys = res["dt_polys"]
        texts = res["rec_texts"]
        
        # Verileri kolay islemek icin bir araya getirip Y koordinatina gore sirala
        items = []
        for i in range(len(texts)):
            # polys[i][0][1] sol üst kosenin Y koordinatidir
            y_top = polys[i][0][1]
            x_left = polys[i][0][0]
            items.append({'y': y_top, 'x': x_left, 'text': texts[i]})
        
        # Y'ye gore sirala (YUKARIDAN ASAGI)
        items.sort(key=lambda x: x['y'])
        
        lines = []
        if not items: return lines

        current_row = [items[0]]
        current_y = items[0]['y']

        for i in range(1, len(items)):
            item = items[i]
            # Eger mevcut satirimizla dikey mesafe esik icindeyse ayni satirdir
            if abs(item['y'] - current_y) <= self.y_threshold:
                current_row.append(item)
            else:
                # Satiri soldan saga (X'e gore) sirala ve birlestir
                current_row.sort(key=lambda x: x['x'])
                lines.append(" ".join([it['text'] for it in current_row]))
                
                # Yeni satira basla
                current_y = item['y']
                current_row = [item]
        
        # Son satiri ekle
        current_row.sort(key=lambda x: x['x'])
        lines.append(" ".join([it['text'] for it in current_row]))
        
        return lines

    def _extract_store_name(self, lines):
        """Ilk 3 satirdaki en anlamli metni magaza adi olarak secer."""
        for line in lines[:3]:
            # Sembolleri ve rakamlari temizle, sadece harf kaldi mi bak
            cleaned = re.sub(r'[^a-zA-Z\sİıĞğÜüŞşÖöçÇ]', '', line).strip()
            if len(cleaned) > 3:
                return cleaned
        return "Bilinmeyen Magaza"

    def _extract_date(self, lines):
        """Tarih desenlerini arar (GG.AA.YYYY vb.)"""
        pattern = r'\d{2}[./-]\d{2}[./-]\d{4}'
        for line in lines:
            match = re.search(pattern, line)
            if match: return match.group()
        return "Bulunamadi"

    def _extract_total_amount(self, lines):
        """Toplam kelimesi gecen satirlardaki en buyuk sayiyi bulur."""
        keywords = ['TOPLAM', 'TUTAR', 'TOTAL', 'TOP', 'TL']
        # 123.45 veya 1.234,56 formatlari
        price_regex = r'\d{1,3}(?:[.,]\d{3})*[.,]\d{2}'
        
        vals = []
        for i, line in enumerate(lines):
            # Anahtar kelime kontrolu
            if any(k in line.upper() for k in keywords):
                # Bu satir ve bir sonraki satiri birlesik tara
                text_to_search = line + (" " + lines[i+1] if i+1 < len(lines) else "")
                for m in re.findall(price_regex, text_to_search):
                    try:
                        # Sayiyi float'a cevir (nokta/virgul temizligi)
                        clean_val = m.replace('.', '').replace(',', '.')
                        vals.append(float(clean_val))
                    except: continue
        
        return max(vals) if vals else 0.0
