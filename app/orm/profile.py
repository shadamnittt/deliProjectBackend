import os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User

def upload_avatar(file, db: Session, user: User):
    try:
        upload_dir = "uploads/avatars/"
        os.makedirs(upload_dir, exist_ok=True)

        file_location = os.path.join(upload_dir, f"{user.username}_avatar.jpg")
        with open(file_location, "wb") as f:
            f.write(file.file.read())

        user.avatar_url = file_location
        db.commit()

        return {"filename": file_location}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error uploading file: {e}")