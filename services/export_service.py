import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from config import settings
from services import db_service

# TR: PDF raporlarini olusturan servis
# EN: Service responsible for generating PDF reports

# TR: Rapor cikti klasorunun var oldugundan emin ol
# EN: Ensure the export output directory exists
EXPORT_DIR = os.path.join(settings.UPLOAD_DIR, "reports")
os.makedirs(EXPORT_DIR, exist_ok=True)

class ReportPDF(FPDF):
    def header(self):
        # TR: PDF baslik bolumu (her sayfa)
        # EN: PDF header section (per page)
        self.set_font("helvetica", "B", 16)
        self.cell(0, 10, "ReceiptShare PDF Report", ln=True, align="C")
        self.ln(5)

    def footer(self):
        # TR: PDF sayfa numarasi altbilgisi
        # EN: PDF footer with page number
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_monthly_pdf(family_id: str, year: int, month: int) -> str | None:
    """Generates a monthly expense report PDF for the entire family."""
    # TR: Ay filtresi ile DataFrame olustur
    # EN: Build dataframe filtered by month
    df = db_service._get_receipts_df(family_id, year, month)
    if df.empty:
        return None

    filename = f"monthly_report_{year}_{month:02d}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)

    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)

    # TR: Rapor basligi
    # EN: Report title
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, f"Monthly Family Expenses ({year}-{month:02d})", ln=True)
    pdf.ln(5)

    # TR: Toplam harcama ozeti
    # EN: Total spending summary
    total_amount = df['total_amount'].sum()
    pdf.set_font("helvetica", size=12)
    pdf.cell(0, 10, f"Total Spent: TRY {total_amount:,.2f}", ln=True)
    
    # TR: Kategori bazli dagilim
    # EN: Category distribution
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Spending by Category:", ln=True)
    pdf.set_font("helvetica", size=11)
    
    cat_sum = df.groupby('category')['total_amount'].sum().sort_values(ascending=False)
    for cat, amount in cat_sum.items():
        pdf.cell(0, 8, f"- {cat}: TRY {amount:,.2f}", ln=True)

    # TR: Uye bazli dagilim
    # EN: Member distribution
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Spending by Member:", ln=True)
    pdf.set_font("helvetica", size=11)
    
    mem_sum = df.groupby('user_name')['total_amount'].sum().sort_values(ascending=False)
    for mem, amount in mem_sum.items():
        pdf.cell(0, 8, f"- {mem}: TRY {amount:,.2f}", ln=True)

    # TR: Tum fisleri tablo halinde yaz
    # EN: Render full receipt table
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Receipt Details:", ln=True)
    
    pdf.set_font("helvetica", size=10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(40, 10, "Date", border=1, fill=True)
    pdf.cell(60, 10, "Store", border=1, fill=True)
    pdf.cell(40, 10, "Category", border=1, fill=True)
    pdf.cell(50, 10, "Amount (TRY)", border=1, fill=True, ln=True)

    for _, row in df.sort_values('date').iterrows():
        pdf.cell(40, 10, str(row['date'])[:10], border=1)
        # Prevent long store names from overflowing
        store_name = str(row['store_name'])[:25]
        pdf.cell(60, 10, store_name, border=1)
        pdf.cell(40, 10, str(row['category']), border=1)
        pdf.cell(50, 10, f"{float(row['total_amount']):,.2f}", border=1, ln=True)

    pdf.output(filepath)
    return filepath


def generate_user_pdf(family_id: str, user_name: str) -> str | None:
    """Generates an expense report PDF for a specific user (all time)."""
    # TR: Tarih filtresi olmadan tum fisleri al
    # EN: Fetch all receipts without date filtering
    all_receipts = [r for r in db_service.db_receipts if r.get("family_id") == family_id]
    if not all_receipts:
        return None
        
    df = pd.DataFrame(all_receipts)
    df['user_name'] = df['uploaded_by'].apply(lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else 'Unknown')
    
    # TR: Kullanici bazli filtre uygula
    # EN: Filter by user
    user_df = df[df['user_name'] == user_name]
    if user_df.empty:
        return None

    filename = f"user_report_{user_name.replace(' ', '_')}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)

    pdf = ReportPDF()
    pdf.add_page()
    
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, f"Expense Report: {user_name}", ln=True)
    pdf.ln(5)

    total_amount = user_df['total_amount'].sum()
    pdf.set_font("helvetica", size=12)
    pdf.cell(0, 10, f"Total Spent (All Time): TRY {total_amount:,.2f}", ln=True)
    pdf.ln(10)

    # TR: Tablo basliklari
    # EN: Table headers
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(40, 10, "Date", border=1, fill=True)
    pdf.cell(80, 10, "Store", border=1, fill=True)
    pdf.cell(50, 10, "Amount (TRY)", border=1, fill=True, ln=True)

    pdf.set_font("helvetica", size=10)
    for _, row in user_df.sort_values('created_at', ascending=False).iterrows():
        pdf.cell(40, 10, str(row.get('date', ''))[:10], border=1)
        store_name = str(row.get('store_name', ''))[:35]
        pdf.cell(80, 10, store_name, border=1)
        pdf.cell(50, 10, f"{float(row.get('total_amount', 0)):,.2f}", border=1, ln=True)

    pdf.output(filepath)
    return filepath


def generate_receipt_pdf(receipt: dict) -> str | None:
    """Generates a detailed PDF for a single receipt."""
    if not receipt:
        return None

    rid = receipt.get("_id", "unknown")
    filename = f"receipt_{rid}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)

    pdf = ReportPDF()
    pdf.add_page()
    
    # TR: Fis bilgisi basligi
    # EN: Receipt header section
    pdf.set_font("helvetica", "B", 16)
    store = str(receipt.get("store_name", "Unknown Store"))
    pdf.cell(0, 10, store, ln=True, align="C")
    
    pdf.set_font("helvetica", size=10)
    pdf.cell(0, 6, f"Date: {receipt.get('date', '-')}", ln=True, align="C")
    category = str(receipt.get("category", "Other"))
    pdf.cell(0, 6, f"Category: {category}", ln=True, align="C")
    
    # TR: Yukleyen bilgisi
    # EN: Uploaded-by info
    uploaded_by = receipt.get("uploaded_by", {})
    user_name = uploaded_by.get("name", "Unknown") if isinstance(uploaded_by, dict) else "Unknown"
    pdf.cell(0, 6, f"Uploaded by: {user_name}", ln=True, align="C")
    
    pdf.ln(10)
    
    # TR: Urun listesi
    # EN: Items list
    items = receipt.get("items", [])
    if items:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "Purchased Items", ln=True)
        pdf.set_font("helvetica", size=10)
        
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(100, 8, "Item", border=1, fill=True)
        pdf.cell(30, 8, "Qty", border=1, fill=True, align="C")
        pdf.cell(60, 8, "Price (TRY)", border=1, fill=True, align="R", ln=True)
        
        for item in items:
            name = str(item.get("name", ""))[:45]
            qty = float(item.get("quantity", 1.0))
            price = float(item.get("price", 0.0))
            
            pdf.cell(100, 8, name, border=1)
            pdf.cell(30, 8, f"{qty:g}", border=1, align="C")
            pdf.cell(60, 8, f"{price:,.2f}", border=1, align="R", ln=True)
            
    pdf.ln(5)
    
    # TR: Toplam tutar
    # EN: Total amount
    pdf.set_font("helvetica", "B", 14)
    total = float(receipt.get("total_amount", 0.0))
    pdf.cell(130, 10, "TOTAL:", align="R")
    pdf.cell(60, 10, f"{total:,.2f} TRY", align="R", ln=True)
    
    # TR: Barkodlar
    # EN: Barcodes
    barcodes = receipt.get("barcodes", [])
    if barcodes:
        pdf.ln(10)
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 8, "Barcodes:", ln=True)
        pdf.set_font("helvetica", size=10)
        for bc in barcodes:
            pdf.cell(0, 6, f"- {bc}", ln=True)
            
    # TR: Garanti bilgisi
    # EN: Warranty details
    warranty = receipt.get("warranty_info", {})
    if warranty and warranty.get("has_warranty"):
        pdf.ln(5)
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(200, 0, 0) # Red for warranty
        months = warranty.get("warranty_months", 0)
        expiry = warranty.get("expiry_date", "")
        pdf.cell(0, 8, f"WARRANTY: {months} Months (Expires: {expiry})", ln=True)
        pdf.set_text_color(0, 0, 0) # Reset color

    pdf.output(filepath)
    return filepath
