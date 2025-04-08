from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import User
from app.service.auth import verify_password, create_access_token, get_password_hash
from app.schemas.user import UserLogin, UserCreate, UserUpdate
from app.orm.user import create_user

router = APIRouter()

print("ZXCXZCZXCZXCZXCCZX")

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=30)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register/")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    new_user = create_user(db, user_data, user_data.password)  # передаём пароль
    return {"email": new_user.email}

@router.delete("/delete/{email}")
def delete_account(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.put("/update/{email}")
def update_account(email: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.new_email:
        user.email = user_update.new_email
    if user_update.new_password:
        user.password_hash = get_password_hash(user_update.new_password)

    db.commit()
    return {"message": "User updated successfully"}
