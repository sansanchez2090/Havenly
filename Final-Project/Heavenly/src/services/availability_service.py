# services/availability_service.py
from datetime import date, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from models.available_date import AvailableDate
from models.property import Property
from models.booking import Booking
from schemas.available_date import AvailableDateCreate, AvailableDateBatchCreate, AvailableDateUpdate


class AvailabilityService:
    
    @staticmethod
    def create_availability(
        db: Session,
        availability_data: AvailableDateCreate,
        user_id: int
    ) -> AvailableDate:
        """
        Create single availability date range for a property
        """
        # Verify property ownership
        property = db.query(Property).filter(
            Property.id == availability_data.property_id,
            Property.region_id == availability_data.region_id,
            Property.user_id == user_id,
            Property.is_active == True
        ).first()
        
        if not property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found or you don't have permission"
            )
        
        # Check for date conflicts with existing availability
        conflict = db.query(AvailableDate).filter(
            AvailableDate.property_id == availability_data.property_id,
            AvailableDate.region_id == availability_data.region_id,
            or_(
                and_(
                    AvailableDate.start_date <= availability_data.end_date,
                    AvailableDate.end_date >= availability_data.start_date
                )
            )
        ).first()
        
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Date range conflicts with existing availability"
            )
        
        # Check for booking conflicts
        booking_conflict = db.query(Booking).filter(
            Booking.property_id == availability_data.property_id,
            Booking.status.in_(['CONFIRMED', 'PENDING']),
            or_(
                and_(
                    Booking.check_in <= availability_data.end_date,
                    Booking.check_out >= availability_data.start_date
                )
            )
        ).first()
        
        if booking_conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Date range conflicts with existing bookings"
            )
        
        # Create availability
        db_availability = AvailableDate(
            start_date=availability_data.start_date,
            end_date=availability_data.end_date,
            is_available=availability_data.is_available,
            property_id=availability_data.property_id,
            region_id=availability_data.region_id
        )
        
        db.add(db_availability)
        db.commit()
        db.refresh(db_availability)
        
        return db_availability
    
    @staticmethod
    def create_batch_availability(
        db: Session,
        batch_data: AvailableDateBatchCreate,
        user_id: int
    ) -> List[AvailableDate]:
        """
        Create multiple availability date ranges for a property
        """
        # Verify property ownership
        property = db.query(Property).filter(
            Property.id == batch_data.property_id,
            Property.region_id == batch_data.region_id,
            Property.user_id == user_id,
            Property.is_active == True
        ).first()
        
        if not property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found or you don't have permission"
            )
        
        created_availabilities = []
        
        try:
            for date_range in batch_data.dates:
                # Check for conflicts
                conflict = db.query(AvailableDate).filter(
                    AvailableDate.property_id == batch_data.property_id,
                    AvailableDate.region_id == batch_data.region_id,
                    or_(
                        and_(
                            AvailableDate.start_date <= date_range.end_date,
                            AvailableDate.end_date >= date_range.start_date
                        )
                    )
                ).first()
                
                if conflict:
                    continue  # Skip conflicting ranges
                
                # Create availability
                db_availability = AvailableDate(
                    start_date=date_range.start_date,
                    end_date=date_range.end_date,
                    is_available=date_range.is_available,
                    property_id=batch_data.property_id,
                    region_id=batch_data.region_id
                )
                
                db.add(db_availability)
                created_availabilities.append(db_availability)
            
            db.commit()
            
            # Refresh all created objects
            for availability in created_availabilities:
                db.refresh(availability)
            
            return created_availabilities
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating batch availability: {str(e)}"
            )
    
    @staticmethod
    def update_availability(
        db: Session,
        availability_id: int,
        region_id: int,
        update_data: AvailableDateUpdate,
        user_id: int
    ) -> Optional[AvailableDate]:
        """
        Update availability date range
        """
        # Get availability with ownership check
        availability = db.query(AvailableDate).join(
            Property, 
            and_(
                Property.id == AvailableDate.property_id,
                Property.region_id == AvailableDate.region_id
            )
        ).filter(
            AvailableDate.id == availability_id,
            AvailableDate.region_id == region_id,
            Property.user_id == user_id,
            Property.is_active == True
        ).first()
        
        if not availability:
            return None
        
        # Check for date conflicts if dates are being updated
        if update_data.start_date or update_data.end_date:
            new_start = update_data.start_date or availability.start_date
            new_end = update_data.end_date or availability.end_date
            
            conflict = db.query(AvailableDate).filter(
                AvailableDate.property_id == availability.property_id,
                AvailableDate.region_id == availability.region_id,
                AvailableDate.id != availability_id,
                or_(
                    and_(
                        AvailableDate.start_date <= new_end,
                        AvailableDate.end_date >= new_start
                    )
                )
            ).first()
            
            if conflict:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Updated date range conflicts with existing availability"
                )
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(availability, field, value)
        
        db.commit()
        db.refresh(availability)
        
        return availability
    
    @staticmethod
    def delete_availability(
        db: Session,
        availability_id: int,
        region_id: int,
        user_id: int
    ) -> bool:
        """
        Delete availability date range
        """
        availability = db.query(AvailableDate).join(
            Property, 
            and_(
                Property.id == AvailableDate.property_id,
                Property.region_id == AvailableDate.region_id
            )
        ).filter(
            AvailableDate.id == availability_id,
            AvailableDate.region_id == region_id,
            Property.user_id == user_id,
            Property.is_active == True
        ).first()
        
        if not availability:
            return False
        
        db.delete(availability)
        db.commit()
        return True
    
    @staticmethod
    def get_property_availability(
        db: Session,
        property_id: int,
        region_id: int,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        is_available: Optional[bool] = None
    ) -> List[AvailableDate]:
        """
        Get availability calendar for a property
        """
        # Verify property ownership
        property = db.query(Property).filter(
            Property.id == property_id,
            Property.region_id == region_id,
            Property.user_id == user_id,
            Property.is_active == True
        ).first()
        
        if not property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found or you don't have permission"
            )
        
        query = db.query(AvailableDate).filter(
            AvailableDate.property_id == property_id,
            AvailableDate.region_id == region_id
        )
        
        # Apply filters
        if start_date:
            query = query.filter(AvailableDate.start_date >= start_date)
        if end_date:
            query = query.filter(AvailableDate.end_date <= end_date)
        if is_available is not None:
            query = query.filter(AvailableDate.is_available == is_available)
        
        return query.order_by(AvailableDate.start_date).all()
    
    @staticmethod
    def block_dates_for_booking(
        db: Session,
        property_id: int,
        region_id: int,
        start_date: date,
        end_date: date
    ) -> bool:
        """
        Block dates when a booking is made (internal use)
        """
        # Find availability ranges that overlap with booking dates
        overlapping = db.query(AvailableDate).filter(
            AvailableDate.property_id == property_id,
            AvailableDate.region_id == region_id,
            AvailableDate.is_available == True,
            or_(
                and_(
                    AvailableDate.start_date <= end_date,
                    AvailableDate.end_date >= start_date
                )
            )
        ).all()
        
        try:
            for availability in overlapping:
                # Case 1: Booking completely within availability range
                if availability.start_date <= start_date and availability.end_date >= end_date:
                    # Split into up to 3 ranges
                    if availability.start_date < start_date:
                        # Create range before booking
                        db.add(AvailableDate(
                            start_date=availability.start_date,
                            end_date=start_date - timedelta(days=1),
                            is_available=True,
                            property_id=property_id,
                            region_id=region_id
                        ))
                    
                    # Create blocked range for booking
                    db.add(AvailableDate(
                        start_date=start_date,
                        end_date=end_date,
                        is_available=False,
                        property_id=property_id,
                        region_id=region_id
                    ))
                    
                    if availability.end_date > end_date:
                        # Create range after booking
                        db.add(AvailableDate(
                            start_date=end_date + timedelta(days=1),
                            end_date=availability.end_date,
                            is_available=True,
                            property_id=property_id,
                            region_id=region_id
                        ))
                    
                    # Delete original range
                    db.delete(availability)
                
                # Case 2: Booking overlaps start of range
                elif availability.start_date < start_date <= availability.end_date:
                    availability.end_date = start_date - timedelta(days=1)
                
                # Case 3: Booking overlaps end of range
                elif availability.start_date <= end_date < availability.end_date:
                    availability.start_date = end_date + timedelta(days=1)
            
            db.commit()
            return True
            
        except Exception:
            db.rollback()
            return False