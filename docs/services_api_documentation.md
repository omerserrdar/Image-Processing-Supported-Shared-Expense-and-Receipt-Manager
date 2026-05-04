# Services API Documentation

This document provides technical details for the internal services used in the Image-Processing-Supported Shared Expense and Receipt Manager project.

---

## 1. Database Service (`services/db_service.py`)
Handles all MongoDB interactions, including user management, family groups, receipt records, and analytics.

### User Management
- **`create_user(name, email, password_hash) -> str`**: Creates a new user and returns their `user_id`.
- **`find_user_by_email(email) -> dict`**: Retrieves a user document by email.
- **`find_user_by_id(user_id) -> dict`**: Retrieves a user document by ID.
- **`update_user_family(user_id, family_id, role)`**: Links a user to a family group.

### Family Management
- **`create_family(name, creator_id, creator_name) -> dict`**: Initializes a new family group.
- **`generate_invite_code(family_id, permanent=False) -> str`**: Creates a join code for the family.
- **`add_member_to_family(family_id, user_id, user_name)`**: Adds a user to an existing family.
- **`update_family_budget(family_id, budget)`**: Sets the monthly spending limit.

### Receipt Management
- **`insert_receipt(data) -> str`**: Saves a receipt document.
- **`get_receipts_by_family(family_id, limit=100) -> list`**: Fetches recent receipts for a family.
- **`link_receipts(rid1, rid2, group_id)`**: Groups two receipts (e.g., store receipt + POS slip).
- **`get_unlinked_receipts(family_id, limit=20)`**: Finds receipts not yet part of a group.

### Analytics (Pandas-based)
- **`get_family_summary(family_id, year, month)`**: Returns total spending, average, and top category.
- **`get_category_distribution(family_id, year, month)`**: Returns spending broken down by category.
- **`get_member_spending(family_id, year, month)`**: Returns spending per family member.
- **`get_daily_spending(family_id, year, month)`**: Returns spending timeline for the month.

---

## 2. OCR Service (`services/ocr_service.py`)
Leverages Google Gemini Vision API for intelligent data extraction and barcode generation.

### Core Functions
- **`async analyze_receipt(image_path) -> dict`**: 
  - **Description**: The primary entry point for receipt analysis.
  - **Logic**: Offloads the heavy API call to a background thread to keep the UI responsive.
  - **Output**: Returns a structured JSON dictionary containing `store_name`, `date`, `total_amount`, `category`, `items`, `barcodes`, and `has_warranty`.

- **`generate_barcode_image(barcode_number, format="code128") -> str`**:
  - **Description**: Converts a text-based barcode/serial number into a scannable image.
  - **Formats**: Supports `ean13`, `ean8` and `code128`.
  - **Return**: The file path to the generated `.png` barcode image.

### AI Prompting Logic
The service uses a specialized prompt (`RECEIPT_PROMPT`) to instruct Gemini to look for:
- Store details and dates.
- Granular item lists.
- **Serial numbers and IMEI** (crucial for warranty certificates).
- Warranty status flags.

---

## 3. Integration Example (Usage in `scan.py`)

```python
from services import ocr_service, db_service

# 1. Analyze image
data = await ocr_service.analyze_receipt(filepath)

# 2. (Optional) Generate barcode image for extracted serial
for bc in data['barcodes']:
    ocr_service.generate_barcode_image(bc)

# 3. Save to database
receipt_id = db_service.insert_receipt(doc)
```
