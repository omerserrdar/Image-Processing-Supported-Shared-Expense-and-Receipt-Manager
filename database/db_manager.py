import sqlite3
import os
from datetime import datetime
import pandas as pd

class DatabaseManager:
    """
    TR: Uygulamanın veritabanı işlemlerini yöneten ana sınıf.
    EN: Main class managing database operations for the application.
    """

    def __init__(self, db_name="receipts.db"):
        """
        TR: Veritabanı bağlantısını başlatır ve tabloları oluşturur.
        EN: Initializes the database connection and creates tables.
        """
        # TR: Projenin kök dizinini bul ve veritabanını oraya sabitle
        # EN: Find project root and fix the database path there
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_name = os.path.join(base_dir, db_name)
        self.init_db()

    def get_connection(self):
        """
        TR: SQLite veritabanına bir bağlantı nesnesi döndürür.
        EN: Returns a connection object to the SQLite database.
        """
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """
        TR: Gerekli tabloları (categories, receipts) oluşturur ve başlangıç verilerini yükler.
        EN: Creates necessary tables (categories, receipts) and loads initial seed data.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # TR: Kategoriler tablosu - Harcamaları gruplandırmak için kullanılır.
        # EN: Categories table - Used to group expenses.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color_code TEXT
            )
        ''')

        # TR: Fişler tablosu - OCR'dan gelen ana verileri saklar.
        # EN: Receipts table - Stores main data extracted via OCR.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_name TEXT,
                receipt_date TEXT,
                total_amount REAL,
                category_id INTEGER,
                image_path TEXT,
                created_at TEXT,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')

        # TR: Eğer tablo boşsa varsayılan kategorileri ekle.
        # EN: Insert default categories if the table is empty.
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            categories = [
                ('Market', '#10b981'),      # Market - Green
                ('Electronics', '#6366f1'), # Electronics - Indigo
                ('Travel', '#f59e0b'),      # Travel - Amber
                ('Food', '#f43f5e'),        # Food - Rose
                ('Other', '#94a3b8')         # Other - Slate
            ]
            cursor.executemany("INSERT INTO categories (name, color_code) VALUES (?, ?)", categories)

        conn.commit()
        conn.close()

    def add_receipt(self, store_name, date, amount, category_name="Other", image_path=""):
        """
        TR: Veritabanına yeni bir fiş kaydı ekler.
        EN: Adds a new receipt record to the database.
        
        Args:
            store_name (str): TR: Mağaza adı | EN: Name of the store
            date (str): TR: Fiş tarihi | EN: Receipt date
            amount (float): TR: Toplam tutar | EN: Total amount
            category_name (str): TR: Kategori adı | EN: Category name
            image_path (str): TR: Görsel dosya yolu | EN: Image file path
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # TR: Verilen kategori adına göre ID'yi bul. Bulamazsa varsayılanı (Other) kullan.
        # EN: Find ID based on category name. Use default (Other) if not found.
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        res = cursor.fetchone()
        category_id = res[0] if res else 5 

        # TR: Şu anki zamanı al | EN: Get current timestamp
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO receipts (store_name, receipt_date, total_amount, category_id, image_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (store_name, date, amount, category_id, image_path, now))
        
        conn.commit()
        conn.close()

    def get_all_receipts(self):
        """
        TR: Tüm fiş kayıtlarını kategori bilgileriyle birlikte getirir.
        EN: Fetches all receipt records along with their category details.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.id, r.receipt_date, r.store_name, c.name, r.total_amount, c.color_code
            FROM receipts r
            JOIN categories c ON r.category_id = c.id
            ORDER BY r.created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_stats(self):
        """
        TR: Dashboard ve Analytics için özet istatistikleri hesaplar.
        EN: Calculates summary statistics for Dashboard and Analytics.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # TR: Toplam harcama tutarı | EN: Total expenditure amount
        cursor.execute("SELECT SUM(total_amount) FROM receipts")
        total = cursor.fetchone()[0] or 0
        
        # TR: Toplam fiş sayısı | EN: Total number of receipts
        cursor.execute("SELECT COUNT(*) FROM receipts")
        count = cursor.fetchone()[0] or 0
        
        # TR: Kategori bazlı harcama dağılımı | EN: Spending distribution by category
        cursor.execute('''
            SELECT c.name, SUM(r.total_amount)
            FROM receipts r
            JOIN categories c ON r.category_id = c.id
            GROUP BY c.name
        ''')
        category_dist = cursor.fetchall()
        
        conn.close()
        return {"total": total, "count": count, "distribution": category_dist}

    def get_analytics_df(self):
        """
        TR: Veritabanındaki fiş ve kategori verilerini Pandas DataFrame olarak döndürür.
        EN: Returns the receipt and category data from the database as a Pandas DataFrame.
        """
        conn = self.get_connection()
        query = '''
            SELECT r.id, r.receipt_date, r.store_name, r.total_amount, c.name as category_name, c.color_code
            FROM receipts r
            JOIN categories c ON r.category_id = c.id
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def delete_receipt(self, receipt_id):
        """
        TR: Verilen ID'ye sahip fiş kaydını siler.
        EN: Deletes the receipt record with the given ID.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM receipts WHERE id = ?", (receipt_id,))
        conn.commit()
        conn.close()

