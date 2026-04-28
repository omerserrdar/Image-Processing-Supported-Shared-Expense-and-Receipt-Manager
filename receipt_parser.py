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
        TR: predict() sonucundaki dt_polys ve rec_texts listelerini kullanarak 
            metinleri aynı Y koordinatına (dikey eksen) göre satırlara dizer.
        EN: Uses the dt_polys and rec_texts lists from the predict() output 
            to align texts into lines based on their Y coordinate (vertical axis).
        """
        if "dt_polys" not in res or "rec_texts" not in res:
            return []

        polys = res["dt_polys"]
        texts = res["rec_texts"]
        
        # TR: Verileri kolay işlemek için bir araya getirip Y koordinatına göre (yukarıdan aşağıya) sırala
        # EN: Group the data together and sort by Y coordinate (top to bottom) for easier processing
        items = []
        for i in range(len(texts)):
            # polys[i][0][1] sol üst kosenin Y koordinatidir
            y_top = polys[i][0][1]
            x_left = polys[i][0][0]
            items.append({'y': y_top, 'x': x_left, 'text': texts[i]})
        
        # TR: Tüm elemanları Y eksenine göre (YUKARIDAN AŞAĞIYA) sırala
        # EN: Sort all items based on the Y axis (TOP TO BOTTOM)
        items.sort(key=lambda x: x['y'])
        
        lines = []
        if not items: return lines

        current_row = [items[0]]
        current_y = items[0]['y']

        for i in range(1, len(items)):
            item = items[i]
            # TR: Eğer mevcut kelime ile satırımız arasındaki dikey mesafe eşik (y_threshold) içindeyse aynı satırdadır
            # EN: If the vertical distance between the current word and our row is within the threshold, they are on the same row
            if abs(item['y'] - current_y) <= self.y_threshold:
                current_row.append(item)
            else:
                # TR: Satır değişti. Önceki satırı soldan sağa (X'e göre) sırala ve birleştir
                # EN: Row changed. Sort the previous row from left to right (based on X) and merge
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
        """
        TR: Fişin ilk 3 satırındaki en anlamlı metni mağaza adı olarak seçer.
        EN: Selects the most meaningful text in the first 3 lines of the receipt as the store name.
        """
        for line in lines[:3]:
            # TR: İstenmeyen sembolleri ve rakamları temizle, sadece harfler kalsın
            # EN: Clean unwanted symbols and numbers, keeping only letters
            cleaned = re.sub(r'[^a-zA-Z\sİıĞğÜüŞşÖöçÇ]', '', line).strip()
            if len(cleaned) > 3:
                return cleaned
        return "Bilinmeyen Magaza"

    def _extract_date(self, lines):
        """
        TR: Tarih desenlerini arar (GG.AA.YYYY, AA/GG/YYYY vb.)
        EN: Searches for date patterns (DD.MM.YYYY, MM/DD/YYYY etc.)
        """
        pattern = r'\d{2}[./-]\d{2}[./-]\d{4}'
        for line in lines:
            match = re.search(pattern, line)
            if match: return match.group()
        return "Bulunamadi"

    def _extract_total_amount(self, lines):
        """
        TR: Toplam, tutar gibi kelimelerin geçtiği satırlardaki en büyük sayıyı bulur.
        EN: Finds the largest number in lines containing keywords like total, amount etc.
        """
        keywords = ['TOPLAM', 'TUTAR', 'TOTAL', 'TOP', 'TL']
        # TR: 123.45 veya 1.234,56 gibi para formatlarını yakalayan regex
        # EN: Regex to catch currency formats like 123.45 or 1,234.56
        price_regex = r'\d{1,3}(?:[.,]\d{3})*[.,]\d{2}'
        
        vals = []
        for i, line in enumerate(lines):
            # TR: Anahtar kelime (TOPLAM, TUTAR) kontrolü
            # EN: Keyword (TOTAL, AMOUNT) check
            if any(k in line.upper() for k in keywords):
                # TR: Olası format hataları için bu satırı ve bir sonraki satırı birleşik tara
                # EN: Scan this line and the next line combined for possible format issues
                text_to_search = line + (" " + lines[i+1] if i+1 < len(lines) else "")
                for m in re.findall(price_regex, text_to_search):
                    try:
                        # TR: Sayıyı ondalıklı (float) formata çevir (nokta/virgül temizliği)
                        # EN: Convert the number to float format (clean dots/commas)
                        clean_val = m.replace('.', '').replace(',', '.')
                        vals.append(float(clean_val))
                    except: continue
        
        return max(vals) if vals else 0.0
