Techstore: Inventory & E-Commerce PWA
A Professional Inventory Management and Shopping System for Small Businesses.

📖 Overview
Techstore is a lightweight, high-performance Progressive Web App (PWA) designed to bridge the gap between inventory management and social commerce. It allows admins to manage stock via a professional dashboard and enables customers to shop and checkout directly via WhatsApp and M-Pesa.

🚀 Key Features
🛒 Customer Experience
PWA Ready: Installable on Android and iOS for an app-like experience.

Smart Bag: Real-time cart management with stock validation.

Dual Checkout:

WhatsApp Integration: Sends formatted order summaries directly to the shop owner.

M-Pesa STK Push: Integrated payment flow for seamless local transactions.

Customer Portal: Track order history by simply entering a phone number.

🛠 Admin Dashboard
Inventory Search: Quickly filter products by name or SKU.

Bulk Management: Upload hundreds of products at once using Excel (.xlsx) or CSV files.

Recycle Bin: Safeguard against accidental deletions with a two-stage removal process.

Dynamic Discounts: Set percentage-based discounts with optional expiration deadlines.

Image Management: Multi-image support per product with a dedicated "Cover Image" selector.

🛠 Tech Stack
Backend: Flask (Python)

Database: SQLAlchemy (SQLite for development / PostgreSQL for production)

Frontend: Jinja2 Templates, Vanilla CSS (Apple-inspired aesthetic)

Data Handling: Pandas, OpenPyXL, XlsxWriter

Payments/Social: Paystack/M-Pesa API & WhatsApp Business API

📂 Project Structure
Plaintext
techstore_pwa/
├── app.py              # Main application logic and routes
├── site.db             # Local SQLite database
├── requirements.txt    # Project dependencies
├── static/
│   ├── css/            # Custom styling
│   ├── js/             # Frontend logic (Cart, PWA Service Worker)
│   └── uploads/        # Product images (organized by ID)
└── templates/          # HTML files (Base, Home, Manage, Portal, etc.)
⚙️ Installation & Setup
Clone the repository:

Bash
git clone https://github.com/mnyabaige/techstore_pwa.git
cd techstore_pwa
Create a Virtual Environment:

Bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
Install Dependencies:

Bash
pip install -r requirements.txt
Run the Application:

Bash
python app.py
Access the app at http://127.0.0.1:5000

🔑 Admin Credentials
To access the management dashboard (/login):

Username: admin

Password: shortcut2026

📊 Bulk Upload Format
When using the Bulk Upload feature, ensure your CSV or Excel file contains the following headers:

sku (Optional)

name (Required)

price (Required)

discount_percent

stock

description

specifications

📝 Roadmap
[ ] Integration with Cloudinary for persistent image storage.

[ ] Automated SMS notifications upon order confirmation.

[ ] Advanced Analytics Dashboard (using Power BI or Plotly).

[ ] Switch to PostgreSQL for production scaling.

👤 Author
Michael Nyairo Graphic Designer & Digital Strategist Website | LinkedIn
