from database import SessionLocal
from created_models.user import User
from created_models.user_role import UserRole
from auth import hash_password

db = SessionLocal()

super_admin = User(
    username="sohaib",
    email="sohaib@gmail.com",
    hashed_password=hash_password("12345"),
    role=UserRole.SUPER_ADMIN
)

db.add(super_admin)
db.commit()
db.refresh(super_admin)
print(f"Super admin created: {super_admin.username} | role: {super_admin.role}")
db.close()