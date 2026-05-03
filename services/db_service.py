"""
TR: Gecici in-memory veritabani servisi (MongoDB yerine).
EN: Temporary in-memory database service (Mocking MongoDB).
"""
import uuid
from datetime import datetime, timedelta
from config import settings

# TR: Bu servis in-memory veri tutar; MongoDB entegrasyonu yoktur
# EN: This service stores data in memory; MongoDB is not wired yet

# --- IN-MEMORY MOCK DB ---
# TR: Uygulama calisma suresince RAM uzerinde tutulan listeler
# EN: In-memory lists that live only for the app lifetime
db_users = []
db_families = []
db_receipts = []

def _generate_id():
    # TR: Basit ve benzersiz ID uretimi
    # EN: Generate a simple unique ID
    return uuid.uuid4().hex

# --- USERS ---
# TR: Kullanici CRUD islemleri
# EN: User CRUD operations
def create_user(name: str, email: str, password_hash: str) -> str:
    # TR: Yeni kullanici kaydi olustur
    # EN: Create a new user record
    user_id = _generate_id()
    db_users.append({
        "_id": user_id,
        "name": name,
        "email": email.lower().strip(),
        "password_hash": password_hash,
        "family_id": None,
        "role": None,
        "language": settings.DEFAULT_LANGUAGE,
        "created_at": datetime.utcnow(),
    })
    return user_id

def find_user_by_email(email: str) -> dict | None:
    # TR: E-posta ile kullanici ara
    # EN: Find user by email
    for u in db_users:
        if u["email"] == email.lower().strip():
            return u.copy()
    return None

def find_user_by_id(user_id: str) -> dict | None:
    # TR: Kullanici ID ile arama
    # EN: Find user by id
    for u in db_users:
        if u["_id"] == user_id:
            return u.copy()
    return None

def update_user_family(user_id: str, family_id: str | None, role: str | None):
    # TR: Kullanici aile/rol bilgisini guncelle
    # EN: Update user's family and role
    for u in db_users:
        if u["_id"] == user_id:
            u["family_id"] = family_id
            u["role"] = role

def update_user_language(user_id: str, language: str):
    # TR: Kullanici dil tercihini guncelle
    # EN: Update user's language preference
    for u in db_users:
        if u["_id"] == user_id:
            u["language"] = language

# --- FAMILIES ---
# TR: Aile gruplari ve uye yonetimi
# EN: Family groups and member management
def create_family(name: str, creator_id: str, creator_name: str) -> dict:
    # TR: Yeni aile olustur ve kurucuyu admin olarak ekle
    # EN: Create family and add creator as admin
    family_id = _generate_id()
    family = {
        "_id": family_id,
        "name": name,
        "created_by": creator_id,
        "members": [{
            "user_id": creator_id,
            "name": creator_name,
            "role": "admin",
            "joined_at": datetime.utcnow(),
        }],
        "invite_codes": [],
        "monthly_budget": 5000,
        "created_at": datetime.utcnow(),
    }
    db_families.append(family)
    update_user_family(creator_id, family_id, "admin")
    return {"family_id": family_id, "name": name}

def generate_invite_code(family_id: str, permanent: bool = False) -> str:
    # TR: Davet kodu uret (gecici veya kalici)
    # EN: Generate an invite code (temporary or permanent)
    import secrets
    code = secrets.token_urlsafe(6).upper()[:8]
    invite = {
        "code": code,
        "permanent": permanent,
        "created_at": datetime.utcnow(),
        "expires_at": None if permanent else datetime.utcnow() + timedelta(hours=24),
    }
    for f in db_families:
        if f["_id"] == family_id:
            f["invite_codes"].append(invite)
    return code

def find_family_by_invite_code(code: str) -> dict | None:
    # TR: Davet koduna gore aile bul
    # EN: Find family by invite code
    now = datetime.utcnow()
    for f in db_families:
        for ic in f["invite_codes"]:
            if ic["code"] == code.upper().strip():
                if ic["permanent"] or (ic["expires_at"] and ic["expires_at"] > now):
                    return f.copy()
    return None

def add_member_to_family(family_id: str, user_id: str, user_name: str):
    # TR: Aileye yeni uye ekle
    # EN: Add a new member to the family
    for f in db_families:
        if f["_id"] == family_id:
            f["members"].append({
                "user_id": user_id,
                "name": user_name,
                "role": "member",
                "joined_at": datetime.utcnow(),
            })
    update_user_family(user_id, family_id, "member")

def get_family(family_id: str) -> dict | None:
    # TR: Aile kaydini dondur
    # EN: Return family record
    for f in db_families:
        if f["_id"] == family_id:
            return f.copy()
    return None

def remove_member_from_family(family_id: str, user_id: str):
    # TR: Uye cikarma islemi
    # EN: Remove a member from the family
    for f in db_families:
        if f["_id"] == family_id:
            f["members"] = [m for m in f["members"] if m["user_id"] != user_id]
    update_user_family(user_id, None, None)

def update_family_budget(family_id: str, budget: float):
    # TR: Aylik butceyi guncelle
    # EN: Update monthly budget
    for f in db_families:
        if f["_id"] == family_id:
            f["monthly_budget"] = budget

# --- RECEIPTS ---
# TR: Fis kayitlari ve birlestirme islemleri
# EN: Receipt records and merge/link operations
def insert_receipt(data: dict) -> str:
    # TR: Yeni fis kaydini ekle
    # EN: Insert a new receipt
    rid = _generate_id()
    data["_id"] = rid
    data["created_at"] = datetime.utcnow()
    db_receipts.append(data.copy())
    return rid

def get_receipts_by_family(family_id: str, limit: int = 100) -> list[dict]:
    # TR: Aileye ait fisleri tarihe gore sirala
    # EN: Fetch family receipts sorted by date
    res = [r.copy() for r in db_receipts if r.get("family_id") == family_id]
    res.sort(key=lambda x: x["created_at"], reverse=True)
    return res[:limit]

def get_receipt_by_id(receipt_id: str) -> dict | None:
    # TR: ID ile fis bul
    # EN: Find receipt by id
    for r in db_receipts:
        if r["_id"] == receipt_id:
            return r.copy()
    return None

def delete_receipt(receipt_id: str):
    # TR: Fis kaydini listeden sil
    # EN: Delete a receipt from the list
    global db_receipts
    db_receipts = [r for r in db_receipts if r["_id"] != receipt_id]

def link_receipts(receipt_id_1: str, receipt_id_2: str, group_id: str):
    # TR: Iki fise ayni group_id vererek bagla
    # EN: Link two receipts by assigning the same group_id
    for r in db_receipts:
        if r["_id"] in [receipt_id_1, receipt_id_2]:
            r["receipt_group_id"] = group_id

def get_linked_receipt(receipt_id: str) -> dict | None:
    # TR: Verilen fisin bagli oldugu diger fise ulas
    # EN: Retrieve the receipt linked to the given one
    base_r = get_receipt_by_id(receipt_id)
    if not base_r or not base_r.get("receipt_group_id"):
        return None
    for r in db_receipts:
        if r.get("receipt_group_id") == base_r["receipt_group_id"] and r["_id"] != receipt_id:
            return r.copy()
    return None

def get_unlinked_receipts(family_id: str, limit: int = 20) -> list[dict]:
    # TR: Henuz birlestirilmemis fisleri getir
    # EN: Fetch receipts that are not linked
    res = [r.copy() for r in db_receipts if r.get("family_id") == family_id and not r.get("receipt_group_id")]
    res.sort(key=lambda x: x["created_at"], reverse=True)
    return res[:limit]

import pandas as pd

# --- ANALYTICS ---
# TR: Analitik hesaplamalar icin pandas tabanli fonksiyonlar
# EN: Analytics helpers based on pandas
def _get_receipts_df(family_id: str, year: int = None, month: int = None) -> pd.DataFrame:
    # TR: Belirli ay icin receipleri filtrele
    # EN: Filter receipts for a given month
    now = datetime.utcnow()
    y = year or now.year
    m = month or now.month
    
    start = datetime(y, m, 1)
    end = datetime(y, m + 1, 1) if m < 12 else datetime(y + 1, 1, 1)
    
    filtered = [r for r in db_receipts if r.get("family_id") == family_id and start <= r["created_at"] < end]
    
    if not filtered:
        return pd.DataFrame()
        
    df = pd.DataFrame(filtered)
    # TR: Yapisal user bilgisini sade bir alan olarak cikar
    # EN: Extract embedded user name into a flat column
    if 'uploaded_by' in df.columns:
        df['user_name'] = df['uploaded_by'].apply(lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else 'Unknown')
    else:
        df['user_name'] = 'Unknown'
        
    # TR: Eksik kategorileri "Other" ile doldur
    # EN: Fill missing categories with "Other"
    if 'category' in df.columns:
        df['category'] = df['category'].fillna('Other')
    else:
        df['category'] = 'Other'
        
    return df

def get_family_summary(family_id: str, year: int = None, month: int = None) -> dict:
    # TR: Toplam, adet, ortalama ve en cok kategori ozeti
    # EN: Summary of total, count, average, and top category
    df = _get_receipts_df(family_id, year, month)
    if df.empty:
        return {"total": 0, "count": 0, "avg": 0, "top_category": "N/A"}
        
    total = float(df['total_amount'].sum())
    count = int(df.shape[0])
    avg = total / count if count > 0 else 0
    
    cat_sum = df.groupby('category')['total_amount'].sum()
    top_cat = cat_sum.idxmax() if not cat_sum.empty else "N/A"
    
    return {"total": total, "count": count, "avg": avg, "top_category": str(top_cat)}

def get_category_distribution(family_id: str, year: int = None, month: int = None) -> list[dict]:
    # TR: Kategoriye gore toplam harcama dagilimi
    # EN: Category-based spending distribution
    df = _get_receipts_df(family_id, year, month)
    if df.empty:
        return []
        
    cat_sum = df.groupby('category')['total_amount'].sum().sort_values(ascending=False)
    return [{"_id": str(k), "total": float(v), "count": 1} for k, v in cat_sum.items()]

def get_member_spending(family_id: str, year: int = None, month: int = None) -> list[dict]:
    # TR: Uyelere gore harcama toplamlarini cikar
    # EN: Compute spending totals by member
    df = _get_receipts_df(family_id, year, month)
    if df.empty:
        return []
        
    mem_sum = df.groupby('user_name')['total_amount'].sum().sort_values(ascending=False)
    return [{"_id": str(k), "total": float(v), "count": 1} for k, v in mem_sum.items()]

def get_daily_spending(family_id: str, year: int = None, month: int = None) -> list[dict]:
    # TR: Gunluk bazda harcama toplami
    # EN: Daily spending totals
    df = _get_receipts_df(family_id, year, month)
    if df.empty:
        return []
        
    if 'date' not in df.columns:
        return []
        
    day_sum = df.groupby('date')['total_amount'].sum().sort_index()
    return [{"_id": str(k), "total": float(v), "count": 1} for k, v in day_sum.items()]

# --- WARRANTY ---
# TR: Garanti takibi icin filtrelenmis fisler
# EN: Warranty-related receipt filtering
def get_warranty_receipts(family_id: str) -> list[dict]:
    # TR: Garanti bilgisi olan fisleri listele
    # EN: List receipts that include warranty info
    res = [r.copy() for r in db_receipts if r.get("family_id") == family_id and r.get("warranty_info", {}).get("has_warranty")]
    res.sort(key=lambda x: x.get("warranty_info", {}).get("expiry_date", ""))
    return res


# =====================================================================
# SEED TEST DATA (Uygulama basladiginda bellekte otomatik olusur)
# =====================================================================
# TR: Demo/test verisi gelistirme amacli eklenir
# EN: Demo/test data added for development convenience
import bcrypt
_test_hash = bcrypt.hashpw("test".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# 1. Test kullanicisi olustur
# TR: Varsayilan test hesabi
# EN: Default test account
_test_user_id = create_user("Test Kullanici", "test@test.com", _test_hash)

# 2. Aile olustur
# TR: Test ailesi
# EN: Test family
_test_family = create_family("Boz Ailesi", _test_user_id, "Test Kullanici")
_test_family_id = _test_family["family_id"]

# 3. Deneme verileri ekle (Market Fisi)
# TR: Ornek market fis kaydi
# EN: Sample market receipt
insert_receipt({
    "family_id": _test_family_id,
    "uploaded_by": {"user_id": _test_user_id, "name": "Test Kullanici"},
    "store_name": "Migros",
    "date": datetime.utcnow().strftime("%Y-%m-%d"),
    "total_amount": 1500.50,
    "currency": "TRY",
    "category": "Market",
    "items": [{"name": "Sut", "quantity": 2, "price": 40}, {"name": "Ekmek", "quantity": 3, "price": 10}],
    "barcodes": [],
    "receipt_type": "store",
    "receipt_group_id": None,
    "image_path": None,
    "warranty_info": {"has_warranty": False},
})

# 4. Deneme verisi (Elektronik ve Garantili)
# TR: Garanti bilgisi olan elektronik fis
# EN: Electronics receipt with warranty info
insert_receipt({
    "family_id": _test_family_id,
    "uploaded_by": {"user_id": _test_user_id, "name": "Test Kullanici"},
    "store_name": "MediaMarkt",
    "date": datetime.utcnow().strftime("%Y-%m-%d"),
    "total_amount": 12500.00,
    "currency": "TRY",
    "category": "Electronics",
    "items": [{"name": "Bluetooth Kulaklik", "quantity": 1, "price": 12500.00}],
    "barcodes": ["8690123456789"],
    "receipt_type": "store",
    "receipt_group_id": None,
    "image_path": None,
    "warranty_info": {
        "has_warranty": True, 
        "warranty_months": 24, 
        "expiry_date": (datetime.utcnow() + timedelta(days=730)).strftime("%Y-%m-%d"), 
        "product_name": "Bluetooth Kulaklik"
    },
})
