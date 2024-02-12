from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from . import models
from .database import SessionLocal

db = SessionLocal()

def cleanStorage(db: Session):
    time_now = datetime.utcnow()
    time_threshold = time_now - timedelta(days=1)
    
    images_to_delete = db.query(models.Images).filter(models.Images.created_at < time_threshold).all()

    if not images_to_delete:
        pass
    else:
        for image in images_to_delete:
            db.delete(image)

    db.commit()


cleanStorage(db)