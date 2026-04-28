# ReceiptShare Enterprise - AI-Powered Expense & Receipt Manager

ReceiptShare is a high-performance, enterprise-grade expense management system that leverages Artificial Intelligence and Computer Vision to digitize financial records. Designed for teams and individuals, it automates the process of extracting data from physical receipts and provides deep analytical insights.

## 🚀 Key Features
- **AI-Powered OCR:** Utilizes PaddleOCR and OpenCV for high-accuracy text extraction from receipts.
- **Enterprise Dashboard:** A modern, dark-themed UI built with Flet, inspired by premium SaaS aesthetics.
- **Team Collaboration:** Create teams, invite members, and share expenses seamlessly.
- **Deep Analytics:** Real-time visualization of spending trends, categorical breakdowns, and budget health.
- **Robust Database:** Architected on MSSQL for reliable data integrity and relational management.

## 🛠 Tech Stack
- **Frontend:** Python, Flet (UI/UX)
- **OCR Engine:** PaddleOCR, OpenCV
- **Backend:** Python 3.12
- **Database:** Microsoft SQL Server (MSSQL)
- **Logic:** SQLAlchemy (ORM), Regex-based Data Parsing

## 📋 Database Architecture
The system consists of 5 core relational tables:
1. `users`: User identity and security.
2. `categories`: Visual categorization and UI color mapping.
3. `receipts`: Central storage for processed financial data and image paths.
4. `teams`: Group structures for shared spending.
5. `team_members`: Role-based membership management.

---

# ReceiptShare Enterprise - Yapay Zeka Destekli Fiş ve Gider Yöneticisi

ReceiptShare, finansal kayıtları dijitalleştirmek için Yapay Zeka ve Bilgisayarlı Görü (Computer Vision) teknolojilerini kullanan, yüksek performanslı bir kurumsal gider yönetim sistemidir. Takımlar ve bireyler için tasarlanan bu uygulama, fiziksel fişlerden veri çıkarma sürecini otomatikleştirir ve derinlemesine analitik içgörüler sunar.

## 🚀 Öne Çıkan Özellikler
- **Yapay Zeka Destekli OCR:** Fişlerden yüksek doğrulukla veri çekmek için PaddleOCR ve OpenCV kullanır.
- **Kurumsal Panel:** Flet ile inşa edilmiş, premium SaaS estetiğinden ilham alan modern karanlık tema arayüzü.
- **Ekip İş Birliği:** Takımlar oluşturun, üyeleri davet edin ve harcamaları sorunsuz bir şekilde paylaşın.
- **Derin Analitik:** Harcama trendlerinin, kategorik dökümlerin ve bütçe sağlığının gerçek zamanlı görselleştirilmesi.
- **Güçlü Veritabanı:** Güvenilir veri bütünlüğü ve ilişkisel yönetim için MSSQL üzerinde yapılandırılmıştır.

## 🛠 Teknoloji Yığını
- **Arayüz:** Python, Flet (UI/UX)
- **OCR Motoru:** PaddleOCR, OpenCV
- **Backend:** Python 3.12
- **Veritabanı:** Microsoft SQL Server (MSSQL)
- **Mantık:** SQLAlchemy (ORM), Regex tabanlı veri işleme

## 📋 Veritabanı Mimarisi
Sistem 5 temel ilişkisel tablodan oluşmaktadır:
1. `users`: Kullanıcı kimliği ve güvenliği.
2. `categories`: Görsel kategorizasyon ve arayüz renk eşleşmeleri.
3. `receipts`: İşlenmiş finansal verilerin ve resim yollarının merkezi deposu.
4. `teams`: Ortak harcamalar için grup yapıları.
5. `team_members`: Rol tabanlı üyelik yönetimi.

---
*Developed by the ReceiptShare Team.*
