"""
TR: MongoDB veritabani servisi.
EN: MongoDB database service.
"""
import uuid
from datetime import datetime, timedelta
import pandas as pd
from pymongo import MongoClient
from config import settings

# --- MONGODB CONNECTION ---
client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB_NAME]

# Collections
users_collection = db["users"]
families_collection = db["families"]
receipts_collection = db["receipts"]

# --- INDEXES ---
# TR: Veri butunlugu icin gerekli indeksler
# EN: Necessary indexes for data integrity
users_collection.create_index("email", unique=True)
families_collection.create_index("invite_codes.code", unique=True)

def _generate_id():
    # TR: Basit ve benzersiz ID uretimi
    # EN: Generate a simple unique ID
    return uuid.uuid4().hex

# --- USERS ---
# TR: Kullanici CRUD islemleri
# EN: User CRUD operations
def create_user(name: str, email: str, password_hash: str) -> str:
    user_id = _generate_id()
    user_doc = {
        "_id": user_id,
        "name": name,
        "email": email.lower().strip(),
        "password_hash": password_hash,
        "family_id": None,
        "role": None,
        "language": settings.DEFAULT_LANGUAGE,
        "created_at": datetime.utcnow(),
    }
    users_collection.insert_one(user_doc)
    return user_id

def find_user_by_email(email: str) -> dict | None:
    return users_collection.find_one({"email": email.lower().strip()})

def find_user_by_id(user_id: str) -> dict | None:
    return users_collection.find_one({"_id": user_id})

def update_user_family(user_id: str, family_id: str | None, role: str | None):
    users_collection.update_one(
        {"_id": user_id},
        {"$set": {"family_id": family_id, "role": role}}
    )

def update_user_language(user_id: str, language: str):
    users_collection.update_one(
        {"_id": user_id},
        {"$set": {"language": language}}
    )

# --- FAMILIES ---
# TR: Aile gruplari ve uye yonetimi
# EN: Family groups and member management
def create_family(name: str, creator_id: str, creator_name: str) -> dict:
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
    families_collection.insert_one(family)
    update_user_family(creator_id, family_id, "admin")
    return {"family_id": family_id, "name": name}

def generate_invite_code(family_id: str, permanent: bool = False) -> str:
    import secrets
    code = secrets.token_urlsafe(6).upper()[:8]
    invite = {
        "code": code,
        "permanent": permanent,
        "created_at": datetime.utcnow(),
        "expires_at": None if permanent else datetime.utcnow() + timedelta(hours=24),
    }
    families_collection.update_one(
        {"_id": family_id},
        {"$push": {"invite_codes": invite}}
    )
    return code

def find_family_by_invite_code(code: str) -> dict | None:
    now = datetime.utcnow()
    # TR: Hem kodu eslesen hem de suresi gecmemis (veya kalici) olan aileyi bul
    # EN: Find family where code matches and is not expired (or is permanent)
    code_upper = code.upper().strip()
    return families_collection.find_one({
        "invite_codes": {
            "$elemMatch": {
                "code": code_upper,
                "$or": [
                    {"permanent": True},
                    {"expires_at": {"$gt": now}}
                ]
            }
        }
    })

def add_member_to_family(family_id: str, user_id: str, user_name: str):
    member_doc = {
        "user_id": user_id,
        "name": user_name,
        "role": "member",
        "joined_at": datetime.utcnow(),
    }
    families_collection.update_one(
        {"_id": family_id},
        {"$push": {"members": member_doc}}
    )
    update_user_family(user_id, family_id, "member")

def get_family(family_id: str) -> dict | None:
    return families_collection.find_one({"_id": family_id})

def remove_member_from_family(family_id: str, user_id: str):
    families_collection.update_one(
        {"_id": family_id},
        {"$pull": {"members": {"user_id": user_id}}}
    )
    update_user_family(user_id, None, None)

def update_family_budget(family_id: str, budget: float):
    families_collection.update_one(
        {"_id": family_id},
        {"$set": {"monthly_budget": budget}}
    )

# --- RECEIPTS ---
# TR: Fis kayitlari ve birlestirme islemleri
# EN: Receipt records and merge/link operations
def insert_receipt(data: dict) -> str:
    rid = _generate_id()
    data["_id"] = rid
    data["created_at"] = datetime.utcnow()
    receipts_collection.insert_one(data)
    return rid

def get_receipts_by_family(family_id: str, limit: int = 100) -> list[dict]:
    cursor = receipts_collection.find({"family_id": family_id}).sort("created_at", -1).limit(limit)
    return list(cursor)

def get_receipt_by_id(receipt_id: str) -> dict | None:
    return receipts_collection.find_one({"_id": receipt_id})

def delete_receipt(receipt_id: str):
    receipts_collection.delete_one({"_id": receipt_id})

def link_receipts(receipt_id_1: str, receipt_id_2: str, group_id: str):
    receipts_collection.update_many(
        {"_id": {"$in": [receipt_id_1, receipt_id_2]}},
        {"$set": {"receipt_group_id": group_id}}
    )

def get_linked_receipt(receipt_id: str) -> dict | None:
    base_r = get_receipt_by_id(receipt_id)
    if not base_r or not base_r.get("receipt_group_id"):
        return None
    return receipts_collection.find_one({
        "receipt_group_id": base_r["receipt_group_id"],
        "_id": {"$ne": receipt_id}
    })

def get_unlinked_receipts(family_id: str, limit: int = 20) -> list[dict]:
    cursor = receipts_collection.find({
        "family_id": family_id,
        "receipt_group_id": {"$in": [None, ""]}
    }).sort("created_at", -1).limit(limit)
    return list(cursor)

# --- ANALYTICS ---
# TR: Analitik hesaplamalar icin pandas tabanli fonksiyonlar
# EN: Analytics helpers based on pandas
def _get_receipts_df(family_id: str, year: int = None, month: int = None) -> pd.DataFrame:
    now = datetime.utcnow()
    y = year or now.year
    m = month or now.month
    
    start = datetime(y, m, 1)
    end = datetime(y, m + 1, 1) if m < 12 else datetime(y + 1, 1, 1)
    
    # TR: Veritabanindan dogrudan tarih filtresi ile cek
    # EN: Fetch directly from database with date filter
    cursor = receipts_collection.find({
        "family_id": family_id,
        "created_at": {"$gte": start, "$lt": end}
    })
    filtered = list(cursor)
    
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
    df = _get_receipts_df(family_id, year, month)
    if df.empty:
        return []
        
    cat_sum = df.groupby('category')['total_amount'].sum().sort_values(ascending=False)
    return [{"_id": str(k), "total": float(v), "count": 1} for k, v in cat_sum.items()]

def get_member_spending(family_id: str, year: int = None, month: int = None) -> list[dict]:
    df = _get_receipts_df(family_id, year, month)
    if df.empty:
        return []
        
    mem_sum = df.groupby('user_name')['total_amount'].sum().sort_values(ascending=False)
    return [{"_id": str(k), "total": float(v), "count": 1} for k, v in mem_sum.items()]

def get_daily_spending(family_id: str, year: int = None, month: int = None) -> list[dict]:
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
    cursor = receipts_collection.find({
        "family_id": family_id,
        "warranty_info.has_warranty": True
    }).sort("warranty_info.expiry_date", 1)
    return list(cursor)


# =====================================================================
# SEED TEST DATA
# =====================================================================
# TR: Veritabani tamamen bossa demo/test verilerini ekle
# EN: Add demo/test data only if the database is completely empty

if users_collection.count_documents({}) == 0:
    import bcrypt
    _test_hash = bcrypt.hashpw("test".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # 1. Test kullanicisi olustur
    _test_user_id = create_user("Test Kullanici", "test@test.com", _test_hash)

    # 2. Aile olustur
    _test_family = create_family("Boz Ailesi", _test_user_id, "Test Kullanici")
    _test_family_id = _test_family["family_id"]

    # 3. Deneme verileri ekle (Market Fisi)
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
