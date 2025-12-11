from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import logging

from models.booking import Booking, BookingStatus
from models.property import Property
from models.payment import Payment, PaymentStatus
from models.user import User
from models.enums import BookingStatus as BookingStatusEnum
from schemas.booking import BookingCreate, BookingUpdate, BookingQuery

logger = logging.getLogger(__name__)


class BookingService:
    def __init__(self, db: Session):
        self.db = db

    def is_property_available(
        self, 
        property_id: int, 
        check_in: date, 
        check_out: date,
        exclude_booking_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si una propiedad está disponible para las fechas solicitadas.
        """
        try:
            property = self.db.query(Property).filter(
                Property.id == property_id,
                Property.is_active == True
            ).first()
            
            if not property:
                logger.warning(f"Property {property_id} not found or inactive")
                return False

            if check_in >= check_out:
                logger.warning("Check-in date must be before check-out date")
                return False

            if check_in < date.today():
                logger.warning("Check-in date cannot be in the past")
                return False

            query = self.db.query(Booking).filter(
                Booking.property_id == property_id,
                Booking.status.in_([BookingStatusEnum.CONFIRMED, BookingStatusEnum.PENDING]),
                or_(
                    and_(
                        Booking.check_in <= check_in,
                        Booking.check_out > check_in
                    ),
                    and_(
                        Booking.check_in < check_out,
                        Booking.check_out >= check_out
                    ),
                    and_(
                        Booking.check_in >= check_in,
                        Booking.check_out <= check_out
                    ),
                    and_(
                        Booking.check_in <= check_in,
                        Booking.check_out >= check_out
                    )
                )
            )

            if exclude_booking_id:
                query = query.filter(Booking.id != exclude_booking_id)

            overlapping_bookings = query.count()

            if overlapping_bookings > 0:
                logger.info(f"Property {property_id} has {overlapping_bookings} overlapping bookings")
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking property availability: {str(e)}")
            raise

    def validate_guest_capacity(
        self, 
        property_id: int, 
        adults: int, 
        children: int, 
        infants: int, 
        pets: int
    ) -> bool:
        """
        Valida que el número de huéspedes no exceda la capacidad de la propiedad.
        """
        property = self.db.query(Property).filter(Property.id == property_id).first()
        
        if not property:
            return False

        if adults > property.max_adults:
            logger.warning(f"Exceeded maximum adults: {adults} > {property.max_adults}")
            return False
        
        if children > property.max_children:
            logger.warning(f"Exceeded maximum children: {children} > {property.max_children}")
            return False
            
        if infants > property.max_infant:
            logger.warning(f"Exceeded maximum infants: {infants} > {property.max_infant}")
            return False
            
        if pets > property.max_pets:
            logger.warning(f"Exceeded maximum pets: {pets} > {property.max_pets}")
            return False

        return True

    def calculate_total_price(
        self, 
        property_id: int, 
        check_in: date, 
        check_out: date,
        adults: int = 1,
        children: int = 0,
        infants: int = 0,
        pets: int = 0
    ) -> Decimal:
        """
        Calcula el precio total de la reserva.
        """
        property = self.db.query(Property).filter(Property.id == property_id).first()
        
        if not property:
            raise ValueError(f"Property {property_id} not found")

        nights = (check_out - check_in).days
        if nights <= 0:
            raise ValueError("Check-out date must be after check-in date")

        base_price = property.price_night * nights

        

        return base_price

    def create_booking(self, booking_data: BookingCreate, user_id: int) -> Booking:
        """
        Crea una nueva reserva.
        """
        try:
            if not self.is_property_available(
                booking_data.property_id, 
                booking_data.check_in, 
                booking_data.check_out
            ):
                raise ValueError("Property not available for selected dates")

            if not self.validate_guest_capacity(
                booking_data.property_id,
                booking_data.guest_adults,
                booking_data.guest_children,
                booking_data.guest_infant,
                booking_data.guest_pets
            ):
                raise ValueError("Exceeds property guest capacity")

            total_price = self.calculate_total_price(
                booking_data.property_id,
                booking_data.check_in,
                booking_data.check_out,
                booking_data.guest_adults,
                booking_data.guest_children,
                booking_data.guest_infant,
                booking_data.guest_pets
            )

            property = self.db.query(Property).filter(Property.id == booking_data.property_id).first()
            if not property:
                raise ValueError(f"Property {booking_data.property_id} not found")

            nights = (booking_data.check_out - booking_data.check_in).days
            
            booking = Booking(
                check_in=booking_data.check_in,
                check_out=booking_data.check_out,
                guest_adults=booking_data.guest_adults,
                guest_children=booking_data.guest_children,
                guest_infant=booking_data.guest_infant,
                guest_pets=booking_data.guest_pets,
                number_nights=nights,
                total_price=total_price,
                status=BookingStatusEnum.PENDING,
                user_id=user_id,
                property_id=booking_data.property_id,
                region_id=property.region_id  
            )

            self.db.add(booking)
            self.db.flush() 
            payment = Payment(
                total=total_price,
                status=PaymentStatus.PENDING,
                booking_id=booking.id,
                currency_id=1,  
                payment_method_id=booking_data.payment_method_id,
                region_id=property.region_id
            )

            self.db.add(payment)
            self.db.commit()
            self.db.refresh(booking)

            logger.info(f"Booking {booking.id} created successfully for user {user_id}")
            return booking

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating booking: {str(e)}")
            raise

    def update_booking_status(
        self, 
        booking_id: int, 
        status: BookingStatusEnum,
        user_id: Optional[int] = None
    ) -> Booking:
        """
        Actualiza el estado de una reserva.
        """
        query = self.db.query(Booking).filter(Booking.id == booking_id)
        
        if user_id:
            query = query.filter(Booking.user_id == user_id)
        
        booking = query.first()
        
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")

        if status == BookingStatusEnum.CANCELED:
            if booking.check_in <= date.today():
                raise ValueError("Cannot cancel booking that has already started")
        
        booking.status = status
        booking.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(booking)
        
        return booking

    def get_user_bookings(
        self, 
        user_id: int,
        status: Optional[BookingStatusEnum] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Booking]:
        """
        Obtiene todas las reservas de un usuario.
        """
        query = self.db.query(Booking).filter(Booking.user_id == user_id)
        
        if status:
            query = query.filter(Booking.status == status)
        
        query = query.order_by(Booking.created_at.desc())
        query = query.offset(offset).limit(limit)
        
        return query.all()

    def get_property_bookings(
        self, 
        property_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Booking]:
        """
        Obtiene todas las reservas de una propiedad en un rango de fechas.
        """
        query = self.db.query(Booking).filter(
            Booking.property_id == property_id,
            Booking.status.in_([BookingStatusEnum.CONFIRMED, BookingStatusEnum.PENDING])
        )
        
        if start_date:
            query = query.filter(Booking.check_out >= start_date)
        
        if end_date:
            query = query.filter(Booking.check_in <= end_date)
        
        return query.order_by(Booking.check_in).all()

    def get_booking_by_id(self, booking_id: int, user_id: Optional[int] = None) -> Optional[Booking]:
        """
        Obtiene una reserva por ID, con opción de verificar propiedad.
        """
        query = self.db.query(Booking).filter(Booking.id == booking_id)
        
        if user_id:
            query = query.filter(Booking.user_id == user_id)
        
        return query.first()

    def get_property_availability(
        self, 
        property_id: int,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        
        bookings = self.get_property_bookings(property_id, start_date, end_date)
        
        availability = []
        current_date = start_date
        
        while current_date <= end_date:
            is_available = True
            
            for booking in bookings:
                if booking.check_in <= current_date < booking.check_out:
                    is_available = False
                    break
            
            availability.append({
                "date": current_date,
                "available": is_available,
                "price": None  
            })
            
            current_date += timedelta(days=1)
        
        return availability

    def check_double_booking(
        self,
        user_id: int,
        property_id: int,
        check_in: date,
        check_out: date,
        exclude_booking_id: Optional[int] = None
    ) -> bool:
       
        query = self.db.query(Booking).filter(
            Booking.user_id == user_id,
            Booking.property_id == property_id,
            Booking.status.in_([BookingStatusEnum.CONFIRMED, BookingStatusEnum.PENDING]),
            or_(
                and_(
                    Booking.check_in <= check_in,
                    Booking.check_out > check_in
                ),
                and_(
                    Booking.check_in < check_out,
                    Booking.check_out >= check_out
                )
            )
        )
        
        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)
        
        return query.count() > 0