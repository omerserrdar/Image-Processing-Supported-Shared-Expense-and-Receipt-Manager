import re

class SmartCategorizer:
    """
    TR: Mağaza adına göre otomatik kategori ataması yapan akıllı sınıf.
    EN: Smart class that performs automatic category assignment based on store name.
    """
    
    def __init__(self):
        # TR: Kategori ve anahtar kelime eşleşmeleri (Keyword Mapping)
        # EN: Category and keyword mappings
        self.mapping = {
            'Market': ['A101', 'BIM', 'SOK', 'MIGROS', 'CARREFOUR'],
            'Food': ['STARBUCKS', 'BURGER KING', 'MCDONALDS', 'RESTAURANT', 'CAFE', 'YEMEKSEPETI'],
            'Electronics': ['VATAN', 'MEDIAMARKT', 'TEKNOSA', 'APPLE'],
            'Travel': ['THY', 'PEGASUS', 'UBER', 'METRO', 'BP', 'SHELL'],
        }
        
        # TR: Türkçe karakterleri İngilizceye çevirmek için tablo (Normalization)
        # EN: Table to convert Turkish characters to English
        self.tr_map = str.maketrans("İıĞğÜüŞşÖöÇç", "IiGgUuSsOoCc")

    def normalize(self, text):
        """
        TR: Metni normalleştirir (Türkçe karakter çevrimi, büyük harf, temizlik).
        EN: Normalizes text (Turkish char conversion, uppercase, cleaning).
        """
        if not text:
            return ""
        # 1. Türkçe karakter çevrimi
        text = text.translate(self.tr_map)
        # 2. Büyük harfe çevir
        text = text.upper()
        # 3. Gereksiz boşlukları temizle
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def get_category(self, store_name):
        """
        TR: Mağaza adına göre kategoriyi döndürür. Eşleşme yoksa "Other" döner.
        EN: Returns category based on store name. Returns "Other" if no match.
        """
        normalized_name = self.normalize(store_name)
        # TR: Karşılaştırma için tüm boşlukları kaldır (Örn: "A 101" -> "A101")
        # EN: Remove all spaces for comparison (e.g. "A 101" -> "A101")
        clean_name = re.sub(r'\s+', '', normalized_name)
        
        for category, keywords in self.mapping.items():
            for keyword in keywords:
                # TR: Anahtar kelimeyi de temizle ve karşılaştır
                # EN: Clean the keyword as well and compare
                clean_keyword = re.sub(r'\s+', '', keyword).upper()
                if clean_keyword in clean_name:
                    return category
                    
        return "Other"
