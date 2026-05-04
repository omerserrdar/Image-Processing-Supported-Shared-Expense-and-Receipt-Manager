# Receipt Scanning Page (scan.py) Documentation

This document describes the technical implementation and internal "API" logic of the `pages/scan.py` module in the Image-Processing-Supported Shared Expense and Receipt Manager project.

## Overview
The `scan.py` file defines the **Receipt Scanning Page** using the NiceGUI framework. Its primary purpose is to allow users to upload receipt images, analyze them using the Gemini-powered OCR service, review/edit the extracted data, and persist the results to the MongoDB database.

---

## Main Components

### 1. `scan_page()`
The entry point function for the page. It sets up the UI layout and handles the high-level state.

- **Purpose**: Initializes the scanning dashboard, user context (family_id, user_id), and the upload zone.
- **Internal State**:
  - `analysis_result`: A dictionary to store the `data` (JSON output from OCR) and `image_path` (local path of the uploaded file).
- **Key Logic**:
  - Checks if the user is in a family (`family_id`).
  - Renders the `ui.upload` component.
  - Defines `handle_upload(e)` to process uploaded files.

### 2. `_show_result(data, lang, family_id, user_id, user_name, image_path, container)`
A private helper function (prefixed with `_`) that renders the editable analysis result card.

- **Arguments**:
  - `data`: The raw JSON data returned from `ocr_service.analyze_receipt`.
  - `lang`: Current UI language (for i18n).
  - `family_id`/`user_id`/`user_name`: Context for saving the record.
  - `image_path`: Path to the original receipt image.
  - `container`: The NiceGUI column/container where the result should be rendered.
- **Functionality**:
  - Clears previous results.
  - Creates input fields (Store Name, Date, Amount, Category) pre-filled with OCR data.
  - Lists items and extracted barcodes.
  - Provides warranty tracking options.
  - Provides a "Merge" option to link this receipt with existing unlinked receipts (e.g., merging a POS slip with a store receipt).

---

## Technical Flows

### A. Upload & Analysis Flow
1.  **File Selection**: User selects a `.png`, `.jpg`, or `.jpeg` file.
2.  **Persistence**: `handle_upload` saves the file to the `uploads/` directory with a unique UUID.
3.  **OCR Trigger**: Calls `await ocr_service.analyze_receipt(filepath)`.
4.  **UI Update**: Once analysis finishes, `_show_result` is triggered to display the data to the user.

### B. Save Flow
Triggered by the `ui.button(t("save_receipt", ...))` in `_show_result`.

1.  **Normalization**: Converts UI inputs (like "Store Receipt" text) into database-friendly values (`"store"` or `"pos"`).
2.  **Warranty Processing**: If "Add Warranty" is checked, calculates the expiry date based on the receipt date and duration.
3.  **Barcode Image Generation**: Calls `ocr_service.generate_barcode_image(bc)` for each extracted barcode to create a visual barcode file.
4.  **Database Insertion**: Calls `db_service.insert_receipt(doc)` with the compiled metadata.
5.  **Linking (Optional)**: If merging is selected, calls `db_service.link_receipts` to group two receipt IDs together.

---

## External Dependencies & Services
The module relies on the following internal services:

- **`services.db_service`**:
  - `insert_receipt(doc)`: Saves the final document.
  - `get_unlinked_receipts(family_id)`: Fetches potential receipts for merging.
  - `link_receipts(...)`: Links two receipts.
- **`services.ocr_service`**:
  - `analyze_receipt(filepath)`: Sends image to Gemini for data extraction.
  - `generate_barcode_image(bc)`: Creates a `.png` barcode file from a string.
- **`config.settings`**: For upload directories and size limits.
- **`theme.style.Theme`**: For consistent glassmorphism design.

---

## UI Interactions (NiceGUI)
- **`ui.upload`**: Configured for `auto_upload=True` and specific mime-types.
- **`ui.bind_visibility_from`**: Used to show/hide warranty fields and merge options dynamically based on checkboxes.
- **`container.clear()`**: Used to reset the result view between multiple scans.
