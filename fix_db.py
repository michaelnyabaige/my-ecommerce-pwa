from app import app, db, Product
import re

def migrate_slugs():
    with app.app_context():
        # Get all products that don't have a slug yet
        products = Product.query.all()
        for p in products:
            if not p.slug:
                # Manual slug generation for migration
                base = re.sub(r'[^\w\s-]', '', p.name).strip().lower()
                p.slug = re.sub(r'[-\s]+', '-', base)
                print(f"Fixed slug for: {p.name} -> {p.slug}")
        
        db.session.commit()
        print("Database migration complete!")

if __name__ == "__main__":
    migrate_slugs()