from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import shutil, os

# --- Database setup ---
Base = declarative_base()
engine = create_engine("sqlite:///apps.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

class AppModel(Base):
    __tablename__ = "apps"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    desc = Column(String, nullable=False)
    filename = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

# --- FastAPI setup ---
app = FastAPI()

# Allow frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for public usage (Netlify, Vercel, etc.)
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Schemas ---
class AppOut(BaseModel):
    id: int
    name: str
    desc: str
    filename: str
    class Config:
        orm_mode = True

# --- Routes ---

@app.get("/apps", response_model=list[AppOut])
def list_apps():
    db = SessionLocal()
    apps = db.query(AppModel).all()
    db.close()
    return apps

@app.post("/apps", response_model=AppOut)
def upload_app(
    name: str = Form(...),
    desc: str = Form(...),
    file: UploadFile = None
):
    if not file:
        raise HTTPException(status_code=400, detail="File required")

    db = SessionLocal()
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    app_entry = AppModel(name=name, desc=desc, filename=file.filename)
    db.add(app_entry)
    db.commit()
    db.refresh(app_entry)
    db.close()
    return app_entry

@app.get("/download/{app_id}")
def download_app(app_id: int):
    db = SessionLocal()
    app_entry = db.query(AppModel).filter(AppModel.id == app_id).first()
    db.close()
    if not app_entry:
        raise HTTPException(status_code=404, detail="App not found")
    filepath = os.path.join(UPLOAD_DIR, app_entry.filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found on server")
    return FileResponse(filepath, filename=app_entry.filename)

@app.delete("/apps/{app_id}")
def delete_app(app_id: int):
    db = SessionLocal()
    app_entry = db.query(AppModel).filter(AppModel.id == app_id).first()
    if not app_entry:
        db.close()
        raise HTTPException(status_code=404, detail="App not found")
    filepath = os.path.join(UPLOAD_DIR, app_entry.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.delete(app_entry)
    db.commit()
    db.close()
    return {"detail": "App deleted"}
