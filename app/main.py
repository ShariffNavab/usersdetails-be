from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import SessionLocal, Bio, init_db

app = FastAPI()
init_db()

class BioInput(BaseModel):
    name: str
    email: str
    age: int
    gender: str

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/save", status_code=201)
def save_bio(bio: BioInput, db: Session = Depends(get_db)):
    try:
        # Check if email already exists
        existing_user = db.query(Bio).filter(Bio.email == bio.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already registered with this email")

        record = Bio(
            name=bio.name,
            email=bio.email,
            age=bio.age,
            gender=bio.gender
        )
        db.add(record)
        db.commit()
        return {"message": "Bio saved successfully"}
    except HTTPException:
        raise  # re-raise the same HTTPException above
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------
# GET /api/users - Fetch all users
# ----------------------------
@app.get("/api/users")
def get_users(db: Session = Depends(get_db)):
    try:
        users = db.query(Bio).all()
        # Convert SQLAlchemy objects to dicts
        result = [
            {"id": u.id, "name": u.name, "email": u.email, "age": u.age, "gender": u.gender}
            for u in users
        ]
        return {"users": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(Bio).filter(Bio.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "age": user.age,
            "gender": user.gender
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user-by-email")
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    try:
        user = db.query(Bio).filter(Bio.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "age": user.age,
            "gender": user.gender
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "healthy", "service": "frontend"}