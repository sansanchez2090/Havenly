from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.property import Property

class PropertyDiscoveryService: 
    """
    @staticmethod
    def list_properties(db: Session,  skip: int = 0, limit: int = 100 ) -> List[Property]:
        return db.query(Property).offset(skip).limit(limit).all()
    """
    
    def list_properties(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        # Filtros básicos
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        property_type_id: Optional[int] = None,
        city_id: Optional[int] = None,
        region_id: Optional[int] = None,
        # Capacidad
        min_adults: Optional[int] = None,
        min_children: Optional[int] = None,
        min_infants: Optional[int] = None,
        min_pets: Optional[int] = None,
        # Amenidades (lista de IDs)
        amenities: Optional[List[int]] = None,
        # Disponibilidad por fechas
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        # Ordenamiento
        sort_by: str = "created_at",  # price, rating, created_at
        sort_order: str = "desc"  # asc, desc
    ) -> List[Property]:
        
        # Query base
        query = db.query(Property)
        
        # 1. FILTRO POR RANGO DE PRECIO
        if min_price is not None or max_price is not None:
            if min_price is not None and max_price is not None:
                query = query.filter(Property.price_night.between(min_price, max_price))
            elif min_price is not None:
                query = query.filter(Property.price_night >= min_price)
            elif max_price is not None:
                query = query.filter(Property.price_night <= max_price)
        
        # 2. FILTRO POR TIPO DE PROPIEDAD
        if property_type_id is not None:
            query = query.filter(Property.property_type_id == property_type_id)
        
        # 3. FILTRO POR UBICACIÓN
        if city_id is not None:
            query = query.filter(Property.city_id == city_id)
        elif region_id is not None:
            query = query.filter(Property.region_id == region_id)
        
        # 4. FILTRO POR CAPACIDAD
        if min_adults is not None:
            query = query.filter(Property.max_adults >= min_adults)
        if min_children is not None:
            query = query.filter(Property.max_children >= min_children)
        if min_infants is not None:
            query = query.filter(Property.max_infant >= min_infants)
        if min_pets is not None:
            query = query.filter(Property.max_pets >= min_pets)
        
        # 5. FILTRO POR AMENIDADES (todas deben estar presentes)
        if amenities:
            # Para cada amenidad, verificamos que la propiedad la tenga
            for amenity_id in amenities:
                # Subquery para verificar si la propiedad tiene la amenidad
                subquery = db.query(Property).join(
                    Property.amenities
                ).filter(
                    Amenity.id == amenity_id,
                    Property.id == Property.id
                ).exists()
                
                query = query.filter(subquery)
        
        # 6. FILTRO POR DISPONIBILIDAD DE FECHAS
        if check_in and check_out:
            if check_in >= check_out:
                raise HTTPException(
                    status_code=400,
                    detail="La fecha de check-in debe ser anterior al check-out"
                )
            
            # Subquery para verificar disponibilidad
            # Una propiedad está disponible si:
            # 1. Tiene fechas disponibles que cubran el rango solicitado
            # 2. No tiene reservas que se superpongan con el rango solicitado
            
            # Primero por fechas disponibles en available_date
            availability_subquery = db.query(AvailableDate).filter(
                AvailableDate.property_id == Property.id,
                AvailableDate.is_available == True,
                AvailableDate.start_date <= check_in,
                AvailableDate.end_date >= check_out
            ).exists()
            
            query = query.filter(availability_subquery)
            
            # También verificar que no haya reservas que se superpongan
            # (esto requiere un join con la tabla booking)
            from src.models.booking import Booking
            booking_conflict_subquery = db.query(Booking).filter(
                Booking.property_id == Property.id,
                Booking.status.in_(['CONFIRMED', 'PENDING']),  # Reservas activas
                or_(
                    # Superposición: la reserva existente se superpone con las fechas solicitadas
                    and_(Booking.check_in <= check_out, Booking.check_out >= check_in)
                )
            ).exists()
            
            query = query.filter(~booking_conflict_subquery)  # NOT EXISTS
        
        # 7. ORDENAMIENTO
        sort_column = getattr(Property, sort_by, Property.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # 8. PAGINACIÓN
        query = query.offset(skip).limit(limit)
        
        # 9. OPTIONAL: Cargar relaciones para evitar N+1 queries
        query = query.options(
            # SQLAlchemy eager loading
            # joinedload(Property.property_type),
            # joinedload(Property.city),
            # joinedload(Property.amenities)
        )
        
        return query.all()
    
   
    @staticmethod
    def get_property():
        pass