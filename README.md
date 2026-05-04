# ReceiptShare — AI-Powered Family Expense & Receipt Manager

> **Scan receipts, share with your family, track spending, protect your warranties.**

## 🚀 Features

- **AI-Powered OCR:** Gemini Vision API extracts store name, date, total, items, and barcodes from receipt images
- **Family Groups:** Create a family, invite members with temporary or permanent codes
- **Per-Member Tracking:** See who spent how much per month
- **Warranty Tracker:** Store barcodes from receipts — show them on your phone at the store
- **Receipt Merging:** Link store receipts with POS receipts
- **Analytics:** Daily spending trends, category distribution, member comparison charts
- **Bilingual:** English + Turkish (switchable in-app)
- **Modern UI:** Glassmorphism dark theme with smooth animations

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | **NiceGUI** (Python → Vue.js/Quasar) |
| Backend | **FastAPI** (built into NiceGUI) |
| AI/OCR | **Google Gemini Vision API** |
| Database | **MongoDB Atlas** |
| Auth | **bcrypt** + NiceGUI sessions |
| Barcode | **python-barcode** |

## 📋 Setup

### 1. Clone & Install
```bash
git clone https://github.com/omerserrdar/Image-Processing-Supported-Shared-Expense-and-Receipt-Manager.git
cd Image-Processing-Supported-Shared-Expense-and-Receipt-Manager
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your actual values:
# - GEMINI_API_KEY (from Google AI Studio)
# - MONGODB_URI (from MongoDB Atlas)
# - SECRET_KEY (any random string)
```

### 3. Run
```bash
python app.py
```
Open http://localhost:8080 in your browser.

## 📂 Project Structure
```
├── app.py              # Main entry point & routing
├── config.py           # Environment configuration
├── pages/
│   ├── login.py        # Login / Register
│   ├── dashboard.py    # Family overview
│   ├── scan.py         # Receipt scanning
│   ├── receipts.py     # Receipt history
│   ├── analytics.py    # Charts & analytics
│   ├── family.py       # Family management
│   └── warranty.py     # Warranty tracker
├── services/
│   ├── db_service.py   # MongoDB operations
│   ├── auth_service.py # Authentication
│   └── ocr_service.py  # Gemini Vision API
├── models/schemas.py   # Pydantic data models
├── theme/style.py      # Design system & CSS
├── i18n/               # EN + TR translations
├── uploads/            # Uploaded receipt images
└── generated_barcodes/ # Generated barcode images
```

---
*Developed by the ReceiptShare Team.*
