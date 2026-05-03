"""
TR: MongoDB Atlas veritabani servisi.
EN: MongoDB Atlas database service.
"""
import uuid
import pandas as pd
from datetime import datetime, timedelta
from pymongo import MongoClient
from config import settings

# --- MONGODB CONNECTION ---
# TR: .env dosyasından çekilen URI ile MongoDB'ye bağlanılır
# EN: Connect to MongoDB using the URI from .env
try:
    client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[settings.MONGODB_DB_NAME]
    users_col = db["users"]
    families_col = db["families"]
    receipts_col = db["receipts"]
except Exception as e:
    print(f"MongoDB Connection Error: {e}")
    users_col = None
    families_col = None
    receipts_col = None


def _generate_id():
    return uuid.uuid4().hex

# --- USERS ---
def create_user(name: str, email: str, password_hash: str) -> str:
    user_id = _generate_id()
    doc = {
        "_id": user_id,
        "name": name,
        "email": email.lower().strip(),
        "password_hash": password_hash,
        "family_id": None,
        "role": None,
        "language": settings.DEFAULT_LANGUAGE,
        "created_at": datetime.utcnow(),
    }
    users_col.insert_one(doc)
    return user_id

def find_user_by_email(email: str) -> dict | None:
    return users_col.find_one({"email": email.lower().strip()})

def find_user_by_id(user_id: str) -> dict | None:
    return users_col.find_one({"_id": user_id})

def update_user_family(user_id: str, family_id: str | None, role: str | None):
    users_col.update_one(
        {"_id": user_id},
        {"$set": {"family_id": family_id, "role": role}}
    )

def update_user_language(user_id: str, language: str):
    users_col.update_one(
        {"_id": user_id},
        {"$set": {"language": language}}
    )

# --- FAMILIES ---
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
    families_col.insert_one(family)
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
    families_col.update_one(
        {"_id": family_id},
        {"$push": {"invite_codes": invite}}
    )
    return code

def find_family_by_invite_code(code: str) -> dict | None:
    now = datetime.utcnow()
    family = families_col.find_one({
        "invite_codes": {
            "$elemMatch": {
                "code": code.upper().strip()
            }
        }
    })
    if not family:
        return None
    
    # Check expiry manually to ensure it's still valid
    for ic in family.get("invite_codes", []):
        if ic["code"] == code.upper().strip():
            if ic["permanent"] or (ic["expires_at"] and ic["expires_at"] > now):
                return family
    return None

def add_member_to_family(family_id: str, user_id: str, user_name: str):
    families_col.update_one(
        {"_id": family_id},
        {"$push": {
            "members": {
                "user_id": user_id,
                "name": user_name,
                "role": "member",
                "joined_at": datetime.utcnow(),
            }
        }}
    )
    update_user_family(user_id, family_id, "member")

def get_family(family_id: str) -> dict | None:
    return families_col.find_one({"_id": family_id})

def remove_member_from_family(family_id: str, user_id: str):
    families_col.update_one(
        {"_id": family_id},
        {"$pull": {"members": {"user_id": user_id}}}
    )
    update_user_family(user_id, None, None)

def update_family_budget(family_id: str, budget: float):
    families_col.update_one(
        {"_id": family_id},
        {"$set": {"monthly_budget": budget}}
    )

# --- RECEIPTS ---
def insert_receipt(data: dict) -> str:
    rid = _generate_id()
    data["_id"] = rid
    data["created_at"] = datetime.utcnow()
    receipts_col.insert_one(data)
    return rid

def get_receipts_by_family(family_id: str, limit: int = 100) -> list[dict]:
    return list(receipts_col.find({"family_id": family_id}).sort("created_at", -1).limit(limit))

def get_receipt_by_id(receipt_id: str) -> dict | None:
    return receipts_col.find_one({"_id": receipt_id})

def delete_receipt(receipt_id: str):
    receipts_col.delete_one({"_id": receipt_id})

def link_receipts(receipt_id_1: str, receipt_id_2: str, group_id: str):
    receipts_col.update_many(
        {"_id": {"$in": [receipt_id_1, receipt_id_2]}},
        {"$set": {"receipt_group_id": group_id}}
    )

def get_linked_receipt(receipt_id: str) -> dict | None:
    base_r = get_receipt_by_id(receipt_id)
    if not base_r or not base_r.get("receipt_group_id"):
        return None
    return receipts_col.find_one({
        "receipt_group_id": base_r["receipt_group_id"],
        "_id": {"$ne": receipt_id}
    })

def get_unlinked_receipts(family_id: str, limit: int = 20) -> list[dict]:
    return list(receipts_col.find({
        "family_id": family_id,
        "receipt_group_id": {"$in": [None, ""]}
    }).sort("created_at", -1).limit(limit))


# --- ANALYTICS ---
def _get_receipts_df(family_id: str, year: int = None, month: int = None) -> pd.DataFrame:
    now = datetime.utcnow()
    y = year or now.year
    m = month or now.month
    
    start = datetime(y, m, 1)
    end = datetime(y, m + 1, 1) if m < 12 else datetime(y + 1, 1, 1)
    
    query = {
        "family_id": family_id,
        "created_at": {"$gte": start, "$lt": end}
    }
    filtered = list(receipts_col.find(query))
    
    if not filtered:
        return pd.DataFrame()
        
    df = pd.DataFrame(filtered)
    if 'uploaded_by' in df.columns:
        df['user_name'] = df['uploaded_by'].apply(lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else 'Unknown')
    else:
        df['user_name'] = 'Unknown'
        
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
def get_warranty_receipts(family_id: str) -> list[dict]:
    query = {
        "family_id": family_id,
        "warranty_info.has_warranty": True
    }
    res = list(receipts_col.find(query))
    res.sort(key=lambda x: x.get("warranty_info", {}).get("expiry_date", ""))
    return res
