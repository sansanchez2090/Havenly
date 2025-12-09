from typing import List
from sqlalchemy.orm import Session
from models.city import City
from models.country import Country

class LocationService:
    @staticmethod
    def list_cities(db: Session, skip: int = 0, limit: int = 100) -> List[City]:
        return db.query(City).offset(skip).limit(limit).all()