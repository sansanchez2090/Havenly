from datetime import date, datetime
from decimal import Decimal
from http.client import HTTPException
from typing import Optional, List
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from starlette import status

from models.amenity import Amenity
from models.available_date import AvailableDate
from models.city import City
from models.property import Property
from models.property_photo import PropertyPhoto
from schemas.property import PropertyCreate, PropertyRes, PropertyUpdate


class PropertyService:
    @staticmethod
    def create_property(
        db: Session, 
        property_data: PropertyCreate, 
        user_id: int
    ) -> Property:
      
        try:
            db_property = Property(
                address=property_data.address,
                description=property_data.description,
                property_type_id=property_data.property_type_id,
                price_night=property_data.price_night,
                max_adults=property_data.max_adults,
                max_children=property_data.max_children,
                max_infant=property_data.max_infant,
                max_pets=property_data.max_pets,
                region_id=property_data.region_id,
                city_id=property_data.city_id,
                user_id=user_id,
                is_active=True
            )
            
            db.add(db_property)
            db.flush()  # Get property ID
            
            if property_data.amenities:
                amenities = db.query(Amenity).filter(
                    Amenity.id.in_(property_data.amenities)
                ).all()
                db_property.amenities.extend(amenities)
            
            if property_data.photo_urls:
                for idx, url in enumerate(property_data.photo_urls):
                    photo = PropertyPhoto(
                        image_url=url,
                        is_primary=(idx == 0),
                        property_id=db_property.id,
                        region_id=property_data.region_id
                    )
                    db.add(photo)
            
            db.commit()
            db.refresh(db_property)
            return db_property
            
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating property: {str(e)}"
            )
    
    @staticmethod
    def update_property(
        db: Session,
        property_id: int,
        region_id: int,
        user_id: int,
        update_data: PropertyUpdate
    ) -> Optional[Property]:
       
        property = db.query(Property).filter(
            Property.id == property_id,
            Property.region_id == region_id,
            Property.user_id == user_id
        ).first()
        
        if not property:
            return None
        
        try:
            update_dict = update_data.model_dump(exclude_unset=True, exclude={"amenities", "photo_urls"})
            
            for field, value in update_dict.items():
                setattr(property, field, value)
            
            if update_data.amenities is not None:
                property.amenities.clear()
                amenities = db.query(Amenity).filter(
                    Amenity.id.in_(update_data.amenities)
                ).all()
                property.amenities.extend(amenities)
            
            if update_data.photo_urls is not None:
                db.query(PropertyPhoto).filter(
                    PropertyPhoto.property_id == property_id,
                    PropertyPhoto.region_id == region_id
                ).delete()
                
                for idx, url in enumerate(update_data.photo_urls):
                    photo = PropertyPhoto(
                        image_url=url,
                        is_primary=(idx == 0),
                        property_id=property_id,
                        region_id=region_id
                    )
                    db.add(photo)
            
            property.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(property)
            return property
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating property: {str(e)}"
            )
    
    @staticmethod
    def delete_property(
        db: Session,
        property_id: int,
        region_id: int,
        user_id: int
    ) -> bool:
      
        property = db.query(Property).filter(
            Property.id == property_id,
            Property.region_id == region_id,
            Property.user_id == user_id
        ).first()
        
        if not property:
            return False
        
        property.is_active = False
        property.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def get_user_properties(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Property]:
      
        return db.query(Property)\
            .filter(Property.user_id == user_id)\
            .order_by(Property.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()