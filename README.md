# Techstore: Inventory & E-Commerce PWA
**A Professional Inventory Management and Shopping System for Small Businesses.**

![Project Banner](https://img.shields.io/badge/Status-Development-orange?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-white?style=for-the-badge&logo=flask)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite)

## 📖 Overview
**Techstore** is a lightweight, high-performance Progressive Web App (PWA) designed to bridge the gap between inventory management and social commerce. It allows admins to manage stock via a professional dashboard and enables customers to shop and checkout directly via **WhatsApp** and **M-Pesa**.

## 🚀 Key Features
### 🛒 Customer Experience
* **PWA Ready:** Installable on Android and iOS for an app-like experience.
* **Smart Bag:** Real-time cart management with stock validation.
* **Dual Checkout:**
    * **WhatsApp Integration:** Sends formatted order summaries directly to the shop owner.
    * **M-Pesa STK Push:** Integrated payment flow for seamless local transactions.
* **Customer Portal:** Track order history by simply entering a phone number.

### 🛠 Admin Dashboard
* **Inventory Search:** Quickly filter products by name or SKU.
* **Bulk Management:** Upload hundreds of products at once using **Excel (.xlsx)** or **CSV** files.
* **Recycle Bin:** Safeguard against accidental deletions with a two-stage removal process.
* **Dynamic Discounts:** Set percentage-based discounts with optional expiration deadlines.
* **Image Management:** Multi-image support per product with a dedicated "Cover Image" selector.

## 🛠 Tech Stack
* **Backend:** Flask (Python)
* **Database:** SQLAlchemy (SQLite for development / PostgreSQL for production)
* **Frontend:** Jinja2 Templates, Vanilla CSS (Apple-inspired aesthetic)
* **Data Handling:** Pandas, OpenPyXL, XlsxWriter
* **Payments/Social:** Paystack/M-Pesa API & WhatsApp Business API

## 📂 Project Structure
```text
techstore_pwa/
├── app.py              # Main application logic and routes
├── site.db             # Local SQLite database
├── requirements.txt    # Project dependencies
├── static/
│   ├── css/            # Custom styling
│   ├── js/             # Frontend logic (Cart, PWA Service Worker)
│   └── uploads/        # Product images (organized by ID)
└── templates/          # HTML files (Base, Home, Manage, Portal, etc.)
