from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from repositories.database import get_db
from services.payment_service import PaymentService
from schemas.payment import PaymentResponse
from utils.get_current_user import get_current_user
from models.user import User

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/booking/{booking_id}/pay", response_model=PaymentResponse)
def pay_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        payment_service = PaymentService(db)
        payment = payment_service.process_payment(booking_id, current_user.id)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing payment")