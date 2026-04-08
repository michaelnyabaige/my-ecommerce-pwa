from app import app, db, Product

with app.app_context():
    db.drop_all()
    db.create_all()
    
    p1 = Product(name="Magic Mouse", price=9500, stock=10, image="https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?q=80&w=500", description="Smooth and wireless.")
    p2 = Product(name="4K USB-C Hub", price=4500, stock=5, image="https://images.unsplash.com/photo-1618410320928-25228d811631?q=80&w=500", description="Essential for MacBooks.")
    
    db.session.add_all([p1, p2])
    db.session.commit()
    print("Database reset with Stock Levels enabled!")