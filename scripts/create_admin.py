from app.database import SessionLocal
from app.models.admin import Admin
from app.utils.auth import hash_password

'''db = SessionLocal()

email = "admin@vinfast.com"
password = "Admin@123"

existing_admin = db.query(Admin).filter(Admin.email == email).first()

if existing_admin:
    print("Admin already exists")
else:
    admin = Admin(
        email=email,
        password_hash=hash_password(password),
        is_active=True
    )
    db.add(admin)
    db.commit()
    print("Admin created successfully")

db.close()'''

def create_admin():
    db = SessionLocal()

    email = "mypersonal.testing01@gmail.com"
    password = "Kishore@2025"

    admin = db.query(Admin).filter(Admin.email == email).first()

    if admin:
        print("❗ Admin already exists")
        return

    new_admin = Admin(
        email=email,
        password_hash=hash_password(password),
        is_active=True
    )

    db.add(new_admin)
    db.commit()
    db.close()

    print("✅ Admin created successfully")

if __name__ == "__main__":
    create_admin()

