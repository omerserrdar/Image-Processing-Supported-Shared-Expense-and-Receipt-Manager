"""
TR: Kimlik doğrulama servisi — kayıt, giriş, oturum yönetimi.
EN: Authentication service — registration, login, session management.
"""

import bcrypt
from services import db_service

# TR: Auth servisinin temel gorevi sifre hashleme ve kullanici dogrulama
# EN: Auth service handles password hashing and user authentication

def hash_password(password: str) -> str:
    """TR: Şifreyi hash'ler | EN: Hashes a password"""
    # TR: bcrypt ile guclu ve tek yonlu hash uret
    # EN: Generate a strong one-way bcrypt hash
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    """TR: Şifreyi doğrular | EN: Verifies a password"""
    # TR: Girilen sifreyi saklanan hash ile dogrula
    # EN: Compare plaintext password against the stored hash
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))


def register(name: str, email: str, password: str) -> dict:
    """
    TR: Yeni kullanıcı kaydı oluşturur.
    EN: Creates a new user registration.

    Returns:
        {"success": True, "user_id": "..."} veya {"success": False, "error": "..."}
    """
    # TR: E-posta daha once kayitli mi kontrol et
    # EN: Check if the email already exists
    existing = db_service.find_user_by_email(email)
    if existing:
        return {"success": False, "error": "email_exists"}

    # TR: Sifreyi hashle ve yeni kayit olustur
    # EN: Hash the password and create a new user record
    password_hash = hash_password(password)
    user_id = db_service.create_user(name, email, password_hash)

    return {"success": True, "user_id": user_id}


def login(email: str, password: str) -> dict:
    """
    TR: Kullanıcı girişi yapar.
    EN: Authenticates a user.

    Returns:
        {"success": True, "user": {...}} veya {"success": False, "error": "..."}
    """
    # TR: E-postaya gore kullaniciyi bul
    # EN: Find user by email
    user = db_service.find_user_by_email(email)
    if not user:
        return {"success": False, "error": "invalid_credentials"}

    # TR: Hash dogrulamasini yap
    # EN: Verify password hash
    if not verify_password(password, user["password_hash"]):
        return {"success": False, "error": "invalid_credentials"}

    # TR: Hassas alanlari response'tan cikar
    # EN: Strip sensitive fields from response
    user.pop("password_hash", None)

    return {"success": True, "user": user}


def get_session_user(storage) -> dict | None:
    """
    TR: NiceGUI storage'dan oturum açmış kullanıcıyı döndürür.
    EN: Returns the logged-in user from NiceGUI storage.
    """
    # TR: Session storage uzerinden kullanici kimligini al
    # EN: Read user id from session storage
    user_id = storage.get("user_id")
    if not user_id:
        return None

    # TR: DB'den kullanici kaydini getir
    # EN: Fetch user record from DB
    user = db_service.find_user_by_id(user_id)
    if user:
        # TR: Guvenlik icin sifre hash'ini kaldir
        # EN: Remove password hash for safety
        user.pop("password_hash", None)
    return user
