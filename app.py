from flask import Flask, render_template, session, redirect, url_for, jsonify, request, send_file
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import datetime
import pandas as pd
import os
import io
import time
import re
from werkzeug.utils import secure_filename
import urllib.parse
import logging

# ========================= APP SETUP =========================
app = Flask(__name__)
app.secret_key = 'nganya-tech-2026-key'

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload Folder
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads', 'products')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

db = SQLAlchemy(app)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================= MODELS =========================
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False) 
    price = db.Column(db.Float, nullable=False) 
    discount_percent = db.Column(db.Integer, default=0)
    discount_deadline = db.Column(db.DateTime, nullable=True)
    image = db.Column(db.String(200), nullable=True) 
    description = db.Column(db.Text, nullable=False)
    specifications = db.Column(db.Text, nullable=True) 
    stock = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade="all, delete-orphan")

    def generate_slug(self):
        new_slug = re.sub(r'[^\w\s-]', '', self.name).strip().lower()
        new_slug = re.sub(r'[-\s]+', '-', new_slug)
        existing = Product.query.filter(Product.slug == new_slug, Product.id != self.id).first()
        if existing:
            self.slug = f"{new_slug}-{int(time.time())}"
        else:
            self.slug = new_slug

    @property
    def is_discount_active(self):
        if self.discount_percent > 0:
            if self.discount_deadline:
                return datetime.utcnow() < self.discount_deadline
            return True
        return False

    @property
    def current_price(self):
        if self.is_discount_active:
            return self.price * (1 - (self.discount_percent / 100))
        return self.price


class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    is_cover = db.Column(db.Boolean, default=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=True)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)
    items_ordered = db.Column(db.Text, nullable=False)
    delivery_notes = db.Column(db.Text, nullable=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)


# ========================= HELPERS =========================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_whatsapp_link(order, cart_items):
    phone_number = "254712345678" 
    items_text = "\n".join([f"- {item['product'].name} (x{item['quantity']})" for item in cart_items])
    
    message = (
        f"👋 *New Order #{order.id}*\n\n"
        f"*Customer:* {order.customer_name or 'N/A'}\n"
        f"*Location:* {order.location or 'N/A'}\n"
        f"*Phone:* {order.customer_phone}\n\n"
        f"*Items:*\n{items_text}\n"
        f"*Total:* {order.total_amount:,.0f} KES\n\n"
        f"Please confirm availability."
    )
    encoded_msg = urllib.parse.quote(message)
    return f"https://wa.me/{phone_number}?text={encoded_msg}"


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ========================= DATABASE INIT =========================
with app.app_context():
    db.create_all()
    logger.info("✅ Database initialized successfully")


# ========================= ROUTES =========================

@app.route('/')
def home():
    products = Product.query.filter_by(is_deleted=False).all()
    return render_template('index.html', products=products)


@app.route('/product/<string:slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    return render_template('product_detail.html', product=product)


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session or not isinstance(session['cart'], dict):
        session['cart'] = {}
    
    data = request.get_json() or {}
    try:
        qty = int(data.get('quantity', 1))
    except:
        qty = 1
    
    product = Product.query.get_or_404(product_id)
    if product.stock < qty:
        return jsonify({"success": False, "message": f"Only {product.stock} available"})

    cart = dict(session['cart']) 
    pid_str = str(product_id)
    cart[pid_str] = cart.get(pid_str, 0) + qty
    
    session['cart'] = cart
    session.modified = True
    return jsonify({"success": True, "cart_count": sum(cart.values())})


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session and isinstance(session['cart'], dict):
        cart = dict(session['cart'])
        pid_str = str(product_id)
        if pid_str in cart:
            del cart[pid_str]
            session['cart'] = cart
            session.modified = True
    return redirect(url_for('checkout'))


@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('checkout'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}
        session['cart'] = {}

    cart_items = []
    total = 0
    for pid_str, qty in cart.items():
        product = Product.query.get(int(pid_str))
        if product:
            subtotal = product.current_price * qty
            cart_items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})
            total += subtotal

    if request.method == 'POST':
        if not cart_items:
            return redirect(url_for('home'))

        new_order = Order(
            customer_name=request.form.get('name'),
            customer_phone=request.form.get('phone'),
            location=request.form.get('location'),
            customer_email=request.form.get('email'),
            total_amount=total,
            items_ordered=", ".join([f"{item['product'].name} (x{item['quantity']})" for item in cart_items]),
            status='Pending'
        )
        db.session.add(new_order)
        db.session.flush() 

        for item in cart_items:
            oi = OrderItem(
                order_id=new_order.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price_at_purchase=item['product'].current_price
            )
            item['product'].stock -= item['quantity']
            db.session.add(oi)

        db.session.commit()
        wa_link = generate_whatsapp_link(new_order, cart_items)
        session.pop('cart', None)
        return render_template('checkout_success.html', order=new_order, wa_link=wa_link)

    return render_template('checkout.html', items=cart_items, total=total)


@app.route('/stk_push', methods=['POST'])
def stk_push():
    phone = request.form.get('phone')
    notes = request.form.get('notes')
    cart_summary = []
    cart_items_for_wa = [] 
    total = 0
    cart = session.get('cart', {})
    
    if not cart or not isinstance(cart, dict):
        return redirect(url_for('home'))

    for pid_str, qty in cart.items():
        item = Product.query.get(int(pid_str))
        if item and item.stock >= qty:
            item.stock -= qty
            cart_summary.append(f"{item.name} (x{qty})")
            cart_items_for_wa.append({'product': item, 'quantity': qty})
            total += (item.current_price * qty)
    
    if not cart_summary:
        return redirect(url_for('home'))

    new_order = Order(
        customer_name="M-Pesa Customer", 
        customer_phone=phone, 
        total_amount=total, 
        items_ordered=", ".join(cart_summary), 
        delivery_notes=notes,
        location="M-Pesa Provided" 
    )
    db.session.add(new_order)
    db.session.commit()
    
    wa_link = generate_whatsapp_link(new_order, cart_items_for_wa)
    session.pop('cart', None)
    return render_template('success.html', order=new_order, wa_link=wa_link)


@app.route('/portal', methods=['GET', 'POST'])
def customer_portal():
    orders = []
    phone_queried = None
    if request.method == 'POST':
        phone_queried = request.form.get('phone')
        if phone_queried:
            orders = Order.query.filter_by(customer_phone=phone_queried).order_by(Order.date_ordered.desc()).all()
    return render_template('portal.html', orders=orders, phone=phone_queried)


@app.route('/admin/manage')
@admin_required
def manage_products():
    query = request.args.get('q', '').strip()
    if query:
        products = Product.query.filter(
            Product.is_deleted == False,
            (Product.name.ilike(f"%{query}%")) | (Product.sku.ilike(f"%{query}%"))
        ).all()
    else:
        products = Product.query.filter_by(is_deleted=False).all()
    return render_template('manage.html', products=products, search_query=query)


@app.route('/admin/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        deadline_raw = request.form.get('discount_deadline')
        deadline = datetime.strptime(deadline_raw, '%Y-%m-%dT%H:%M') if deadline_raw else None
        
        new_p = Product(
            sku=request.form.get('sku'),
            name=request.form.get('name'),
            price=float(request.form.get('price')),
            discount_percent=int(request.form.get('discount_percent', 0)),
            discount_deadline=deadline,
            stock=int(request.form.get('stock', 0)),
            description=request.form.get('description'),
            specifications=request.form.get('specifications')
        )
        new_p.generate_slug() 
        db.session.add(new_p)
        db.session.flush()

        cover_index = int(request.form.get('cover_index', 0))
        files = request.files.getlist('product_images')
        
        for index, file in enumerate(files):
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = secure_filename(f"prod_{new_p.id}_img_{index}_{int(time.time())}.{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_img = ProductImage(filename=filename, product_id=new_p.id, is_cover=(index == cover_index))
                db.session.add(new_img)

        db.session.commit()
        return redirect(url_for('manage_products'))
    return render_template('add_product.html')


@app.route('/admin/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        deadline_raw = request.form.get('discount_deadline')
        product.sku = request.form.get('sku')
        product.name = request.form.get('name')
        product.generate_slug() 
        product.price = float(request.form.get('price'))
        product.discount_percent = int(request.form.get('discount_percent', 0))
        product.discount_deadline = datetime.strptime(deadline_raw, '%Y-%m-%dT%H:%M') if deadline_raw else None
        product.stock = int(request.form.get('stock', 0))
        product.description = request.form.get('description')
        product.specifications = request.form.get('specifications')

        files = request.files.getlist('product_images')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(f"prod_{product.id}_edit_{int(time.time())}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                db.session.add(ProductImage(filename=filename, product_id=product.id))
        
        db.session.commit()
        return redirect(url_for('manage_products'))
    return render_template('edit_product.html', product=product)


@app.route('/admin/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_deleted = True
    db.session.commit()
    return redirect(url_for('manage_products'))


@app.route('/admin/bin')
@admin_required
def recycle_bin():
    deleted_products = Product.query.filter_by(is_deleted=True).all()
    return render_template('bin.html', products=deleted_products)


@app.route('/admin/restore/<int:product_id>', methods=['POST'])
@admin_required
def restore_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_deleted = False
    db.session.commit()
    return redirect(url_for('recycle_bin'))


@app.route('/admin/permanent_delete/<int:product_id>', methods=['POST'])
@admin_required
def permanent_delete(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('recycle_bin'))


@app.route('/admin/orders')
@admin_required
def view_orders():
    orders = Order.query.order_by(Order.date_ordered.desc()).all()
    total_rev = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    order_count = len(orders)
    avg_order = total_rev / order_count if order_count > 0 else 0
    return render_template('orders.html', orders=orders, total_revenue=total_rev, order_count=order_count, avg_order=avg_order)


@app.route('/admin/export_orders')
@admin_required
def export_orders():
    orders = Order.query.order_by(Order.date_ordered.desc()).all()
    data = []
    for o in orders:
        data.append({
            "ID": o.id,
            "Date": o.date_ordered.strftime('%Y-%m-%d %H:%M'),
            "Phone": o.customer_phone,
            "Items": o.items_ordered,
            "Total": o.total_amount
        })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="Orders.xlsx")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == 'shortcut2026':
            session['is_admin'] = True
            return redirect(url_for('manage_products'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('home'))


@app.route('/admin/download_template')
@admin_required
def download_template():
    columns = ['sku', 'name', 'price', 'discount_percent', 'stock', 'description', 'specifications']
    df = pd.DataFrame(columns=columns)
    sample_data = {
        'sku': 'VITZ-001', 'name': 'Sample Product', 'price': 1500,
        'discount_percent': 0, 'stock': 10, 'description': 'Sample description',
        'specifications': 'Sample specs'
    }
    df = pd.concat([df, pd.DataFrame([sample_data])], ignore_index=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Products')
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="product_upload_template.xlsx")


@app.route('/admin/bulk_upload', methods=['POST'])
@admin_required
def bulk_upload():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return "Unsupported file format. Please upload CSV or Excel.", 400
            
        df.columns = [c.strip().lower() for c in df.columns]
        
        required = ['name', 'price']
        if not all(col in df.columns for col in required):
            return f"Missing required columns: {required}", 400

        with db.session.no_autoflush:
            for index, row in df.iterrows():
                sku_val = str(row.get('sku', ''))
                if sku_val.lower() == 'nan' or not sku_val:
                    sku_val = None

                new_p = Product(
                    sku=sku_val,
                    name=str(row['name']),
                    price=float(row['price']),
                    discount_percent=int(row.get('discount_percent', 0)),
                    stock=int(row.get('stock', 0)),
                    description=str(row.get('description', '')),
                    specifications=str(row.get('specifications', ''))
                )
                base_slug = re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', new_p.name).strip().lower())
                new_p.slug = f"{base_slug}-{int(time.time()) + index}"
                db.session.add(new_p)
        
        db.session.commit()
        return redirect(url_for('manage_products'))

    except Exception as e:
        db.session.rollback()
        logger.error(f"Bulk upload error: {e}")
        return f"Error processing file: {str(e)}", 500


# ========================= RUN APP =========================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
