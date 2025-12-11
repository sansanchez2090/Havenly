from datetime import date
from decimal import Decimal
from http.client import HTTPException
from typing import Optional, List
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from models.amenity import Amenity
from models.available_date import AvailableDate
from models.city import City
from models.property import Property
from schemas.property import PropertyRes


class PropertyDiscoveryService:
    
    @staticmethod
    def get_property(db: Session, property_id: int) -> Optional[PropertyRes]:
        """
        Get property by ID with related data and transform to PropertyRes
        """
        prop = db.query(Property)\
            .options(
                joinedload(Property.city).joinedload(City.country),
                joinedload(Property.region),
                joinedload(Property.photos),
                joinedload(Property.owner)
            )\
            .filter(Property.id == property_id)\
            .first()
        
        if not prop:
            return None
        
        # Extract photo URLs
        photo_urls = [photo.url for photo in prop.photos] if prop.photos else []
        
        # Get country name
        country_name = ""
        if prop.city and prop.city.country:
            country_name = prop.city.country.name
        
        # Get host name
        host_name = ""
        if prop.owner:
            host_name = f"{prop.owner.first_name} {prop.owner.last_name}"
        
        # Create PropertyRes
        return PropertyRes(
            id=prop.id,
            address=prop.address,
            description=prop.description,
            property_type_id=prop.property_type_id,
            price_night=prop.price_night,
            max_adults=prop.max_adults,
            max_children=prop.max_children,
            max_infant=prop.max_infant,
            max_pets=prop.max_pets,
            city=prop.city.name if prop.city else "",
            country=country_name,
            region=prop.region.name if prop.region else "",
            photos=photo_urls,
            host=host_name,
            host_id=str(prop.user_id)  # or int depending on your schema
        )

    @staticmethod
    def list_properties(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        property_type_id: Optional[int] = None,
        city_id: Optional[int] = None,
        region_id: Optional[int] = None,
        min_adults: Optional[int] = None,
        min_children: Optional[int] = None,
        min_infants: Optional[int] = None,
        min_pets: Optional[int] = None,
        amenities: Optional[List[int]] = None,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> List[PropertyRes]:
        
        query = db.query(Property)
        
        # Price filter
        if min_price is not None or max_price is not None:
            if min_price is not None and max_price is not None:
                query = query.filter(Property.price_night.between(min_price, max_price))
            elif min_price is not None:
                query = query.filter(Property.price_night >= min_price)
            elif max_price is not None:
                query = query.filter(Property.price_night <= max_price)
        
        # Property type filter
        if property_type_id is not None:
            query = query.filter(Property.property_type_id == property_type_id)
        
        # Location filters
        if city_id is not None:
            query = query.filter(Property.city_id == city_id)
        elif region_id is not None:
            query = query.filter(Property.region_id == region_id)
        
        # Capacity filters
        if min_adults is not None:
            query = query.filter(Property.max_adults >= min_adults)
        if min_children is not None:
            query = query.filter(Property.max_children >= min_children)
        if min_infants is not None:
            query = query.filter(Property.max_infant >= min_infants)
        if min_pets is not None:
            query = query.filter(Property.max_pets >= min_pets)
        
        # Amenities filter
        if amenities:
            for amenity_id in amenities:
                subquery = db.query(Property).join(
                    Property.amenities
                ).filter(
                    Amenity.id == amenity_id,
                    Property.id == Property.id
                ).exists()
                query = query.filter(subquery)
        
        # Availability filter
        if check_in and check_out:
            if check_in >= check_out:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=400,
                    detail="Check-in date must be before check-out"
                )
            
            availability_subquery = db.query(AvailableDate).filter(
                AvailableDate.property_id == Property.id,
                AvailableDate.is_available == True,
                AvailableDate.start_date <= check_in,
                AvailableDate.end_date >= check_out
            ).exists()
            query = query.filter(availability_subquery)
            
            from models.booking import Booking
            booking_conflict_subquery = db.query(Booking).filter(
                Booking.property_id == Property.id,
                Booking.status.in_(['CONFIRMED', 'PENDING']),
                or_(
                    and_(Booking.check_in <= check_out, Booking.check_out >= check_in)
                )
            ).exists()
            query = query.filter(~booking_conflict_subquery)
        
        # Sorting
        sort_column = getattr(Property, sort_by, Property.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Eager loading
        query = query.options(
            joinedload(Property.city).joinedload(City.country),
            joinedload(Property.region),
            joinedload(Property.photos),
            joinedload(Property.owner)
        )
        
        # Get properties
        properties = query.offset(skip).limit(limit).all()
        
        # Transform to PropertyRes
        result: List[PropertyRes] = []
        for prop in properties:
            # Extract photo URLs
            photo_urls = [photo.url for photo in prop.photos] if prop.photos else []
            
            # Get country name
            country_name = ""
            if prop.city and prop.city.country:
                country_name = prop.city.country.name
            
            # Get host name
            host_name = ""
            if prop.owner:
                host_name = f"{prop.owner.first_name} {prop.owner.last_name}"
            
            # Create PropertyRes
            property_res = PropertyRes(
                id=prop.id,
                address=prop.address,
                description=prop.description,
                property_type_id=prop.property_type_id,
                price_night=prop.price_night,
                max_adults=prop.max_adults,
                max_children=prop.max_children,
                max_infant=prop.max_infant,
                max_pets=prop.max_pets,
                city=prop.city.name if prop.city else "",
                country=country_name,
                region=prop.region.name if prop.region else "",
                photos=photo_urls,
                host=host_name,
                host_id=str(prop.user_id)  # Convert to string as defined in schema
            )
            result.append(property_res)
        
        return result
       