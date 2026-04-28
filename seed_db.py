from database.db_manager import DatabaseManager
import os

# TR: Veritabanı yöneticisini başlat (Kök dizindeki receipts.db)
# EN: Initialize database manager (receipts.db in root directory)
db = DatabaseManager("receipts.db")

# TR: Harcama verileri (Büyük bir set oluşturuyoruz)
# EN: Expense data (Creating a large dummy dataset)
receipts = [
    ("MOC CAFE", "2026-06-20", 205.00, "Yemek"),
    ("MIGROS JET", "2026-04-25", 154.00, "Market"),
    ("OZCAN KARDESLER", "2026-05-12", 101.00, "Market"),
    ("STARBUCKS", "2026-04-20", 115.50, "Yemek"),
    ("TEKNOSA", "2026-04-18", 2450.00, "Elektronik"),
    ("SHELL", "2026-04-15", 850.00, "Seyahat"),
    ("H&M", "2026-04-12", 420.00, "Diğer"),
    ("BURGER KING", "2026-04-10", 185.00, "Yemek"),
    ("ZARA", "2026-04-08", 1250.00, "Diğer"),
    ("GETIR", "2026-04-07", 340.00, "Market"),
    ("THY", "2026-04-05", 4200.00, "Seyahat"),
    ("NETFLIX", "2026-04-01", 150.00, "Elektronik"),
    ("KOCTAS", "2026-03-28", 560.00, "Diğer")
]

print("Veritabanı güncelleniyor...")

for store, date, amount, category in receipts:
    db.add_receipt(store, date, amount, category_name=category)
    print(f"Eklendi: {store} - {amount} TL")

print("\nVeritabanı senkronizasyonu tamamlandı!")
