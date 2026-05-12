# ReceiptShare - AI-Powered Family Expense & Receipt Manager

ReceiptShare is a NiceGUI application that helps families scan receipts, share expenses, track spending, and store warranty barcodes. It combines a modern UI with OCR powered by Google Gemini Vision and stores data in MongoDB Atlas.

## Features

- AI-powered OCR for store name, date, totals, items, and barcodes
- Family groups with invite codes (temporary or permanent)
- Per-member and monthly spending tracking
- Warranty barcode storage for quick in-store access
- Receipt merging between store and POS receipts
- Analytics for trends and category distributions
- Bilingual UI (English and Turkish)

## Tech Stack

| Layer | Technology |
|---|---|
| UI | NiceGUI (Python to Vue.js/Quasar) |
| Backend | FastAPI (built into NiceGUI) |
| AI/OCR | Google Gemini Vision API |
| Database | MongoDB Atlas |
| Auth | bcrypt and NiceGUI sessions |
| Barcode | python-barcode |

## Requirements

- Python 3.x
- Google Gemini API key
- MongoDB Atlas cluster and connection string

## Quick Start

1) Clone and install
```bash
git clone https://github.com/omerserrdar/Image-Processing-Supported-Shared-Expense-and-Receipt-Manager.git
cd Image-Processing-Supported-Shared-Expense-and-Receipt-Manager
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2) Configure environment
```bash
cp .env.example .env
```
Update the values in .env as needed.

3) Run the app
```bash
python app.py
```
Open http://localhost:8080 in your browser.

## Configuration

The default configuration is defined in [/.env.example](.env.example). Key variables:

| Variable | Description |
|---|---|
| APP_PORT | Port for the web server |
| SECRET_KEY | Secret for session and token generation |
| DEFAULT_LANGUAGE | UI language (en or tr) |
| GEMINI_API_KEY | Google Gemini API key |
| GEMINI_MODEL | Gemini model name |
| MONGODB_URI | MongoDB Atlas connection string |
| MONGODB_DB_NAME | Database name |

## Project Structure

```
├── app.py              # Main entry point and routing
├── config.py           # Environment configuration
├── pages/
│   ├── login.py        # Login and registration
│   ├── dashboard.py    # Family overview
│   ├── scan.py         # Receipt scanning
│   ├── receipts.py     # Receipt history
│   ├── analytics.py    # Charts and analytics
│   ├── family.py       # Family management
│   └── warranty.py     # Warranty tracker
├── services/
│   ├── db_service.py   # MongoDB operations
│   ├── auth_service.py # Authentication
│   └── ocr_service.py  # Gemini Vision API integration
├── models/schemas.py   # Pydantic data models
├── theme/style.py      # Design system and CSS
├── i18n/               # EN and TR translations
├── uploads/            # Uploaded receipt images (runtime data)
└── generated_barcodes/ # Generated barcode images (runtime data)
```

## Documentation

- [docs/scan_page_api.md](docs/scan_page_api.md)
- [docs/scan_page_api_tr.md](docs/scan_page_api_tr.md)
- [docs/services_api_documentation.md](docs/services_api_documentation.md)
- [docs/services_api_documentation_tr.md](docs/services_api_documentation_tr.md)

## Changelog

- [CHANGELOG_DB.md](CHANGELOG_DB.md)

## Contributing

Issues and pull requests are welcome. Please open an issue first for large changes.
