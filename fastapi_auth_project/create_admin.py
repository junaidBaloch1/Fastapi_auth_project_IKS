from database import SessionLocal
from created_models.user import User
from created_models.user_role import UserRole
from auth import hash_password

db = SessionLocal()

admin = User(
    username="sohaib",
    email="sohaib@gmail.com",
    hashed_password=hash_password("12345"),
    role=UserRole.ADMIN
)

db.add(admin)
db.commit()
db.refresh(admin)
print(f"Admin created: {admin.username} | role: {admin.role}")
db.close()