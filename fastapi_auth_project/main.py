from fastapi import FastAPI
from database import engine, Base
from routes import router

# Create all tables in the database on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI Auth",
    description="Register, Login, Logout with JWT",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Auth API is running"}