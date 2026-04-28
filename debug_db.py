import sqlite3
import os

# TR: Veritabanı yolunu bul
# EN: Find the database path
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "receipts.db")

print(f"Kontrol edilen veritabanı yolu: {db_path}")

if not os.path.exists(db_path):
    print("HATA: Veritabanı dosyası fiziksel olarak mevcut değil!")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Kategorileri kontrol et
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        print(f"\nKategoriler ({len(categories)} adet):")
        for cat in categories:
            print(cat)
            
        # Fişleri kontrol et
        cursor.execute("SELECT * FROM receipts")
        receipts = cursor.fetchall()
        print(f"\nFişler ({len(receipts)} adet):")
        for rec in receipts:
            print(rec)
            
        conn.close()
    except Exception as e:
        print(f"SQL HATASI: {e}")

print("\n--- Kontrol Bitti ---")
