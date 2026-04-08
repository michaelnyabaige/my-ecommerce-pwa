import urllib.parse
from flask import url_for, render_template
from flask_mail import Message # Assuming you use Flask-Mail

def process_order_notifications(order, items):
    """
    order: The order database object
    items: List of product objects in the order
    """
    
    # 1. Format the WhatsApp Message
    store_phone = "254712345678" # Your business number
    item_list = "\n".join([f"- {item.product.name} (x{item.quantity})" for item in items])
    
    raw_message = (
        f"🚀 *New Order #{order.id}*\n\n"
        f"Customer: {order.customer_name}\n"
        f"Items:\n{item_list}\n\n"
        f"*Total: {order.total_amount:,.0f} KES*\n"
        f"Delivery to: {order.location}\n\n"
        f"Please confirm availability to proceed with M-Pesa."
    )
    
    # Encode for URL
    whatsapp_url = f"https://wa.me/{store_phone}?text={urllib.parse.quote(raw_message)}"

    # 2. Prepare the Email (Optional: using Flask-Mail)
    # msg = Message(f"Order Confirmation #{order.id}",
    #               sender="noreply@yourstore.com",
    #               recipients=[order.customer_email])
    # msg.html = render_template('emails/order_confirm.html', order=order, items=items)
    
    return whatsapp_url