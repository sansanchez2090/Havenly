from sqlalchemy.orm import Session
from models.payment import Payment, PaymentStatus
from models.booking import Booking, BookingStatus

class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def process_payment(self, booking_id: int, user_id: int) -> Payment:
        
        booking = self.db.query(Booking).filter(
            Booking.id == booking_id,
            Booking.user_id == user_id
        ).first()
        
        if not booking:
            raise ValueError("Booking not found or access denied")
        
        existing_payment = self.db.query(Payment).filter(
            Payment.booking_id == booking_id,
            Payment.status == PaymentStatus.SUCCESSFUL
        ).first()
        
        if existing_payment:
            raise ValueError("Booking already has a successful payment")
        
        payment = Payment(
            total=booking.total_price,
            status=PaymentStatus.SUCCESSFUL, 
            booking_id=booking.id,
            currency_id=1,  
            payment_method_id=1, 
            region_id=booking.region_id,
            transaction_id=f"txn_{booking.id}_{booking.user_id}"  
        )
        
        self.db.add(payment)
        
        booking.status = BookingStatus.CONFIRMED
        
        self.db.commit()
        self.db.refresh(payment)
        
        return payment