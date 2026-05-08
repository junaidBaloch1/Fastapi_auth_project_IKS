from fastapi import FastAPI
from database import engine, Base
from routes.routes import router, admin_router, user_router
from routes.super_admin_routes import super_router          # ← add this
from routes.org_routes import org_router, invite_router
from fastapi.middleware.cors import CORSMiddleware


# Create all tables in the database on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI Auth + Role Based Access Control RBAC",
    description="Register, Login, Logout with JWT",
    version="1.0.0"
)

app.include_router(router)        # /auth/*  — public
app.include_router(user_router)   # /user/*  — logged in users
app.include_router(admin_router)  # /admin/* — admin only
app.include_router(super_router)
app.include_router(org_router)    # /org/*
app.include_router(invite_router) # /invitations/*


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Auth API is running"}


