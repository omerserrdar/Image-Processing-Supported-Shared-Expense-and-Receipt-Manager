import sqlite3
import os

db_path = r"c:\Users\DAK\Desktop\İpt Ocr\receipts.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    translations = {
        'Elektronik': 'Electronics',
        'Seyahat': 'Travel',
        'Yemek': 'Food',
        'Diğer': 'Other'
    }
    
    for tr, en in translations.items():
        cursor.execute("UPDATE categories SET name = ? WHERE name = ?", (en, tr))
        print(f"Updated {tr} to {en}")
        
    conn.commit()
    conn.close()
    print("Database categories translated successfully.")
else:
    print("Database file not found.")
