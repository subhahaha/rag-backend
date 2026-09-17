from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from app.schemas.booking import BookingCreate
from app.services.booking_service import create_booking


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.post("/")
def create_booking_endpoint(
    booking: BookingCreate,
    db: Session = Depends(get_db),
) -> dict[str, str | int]:
    new_booking = create_booking(
        db=db,
        booking=booking,
    )

    return {
        "id": new_booking.id,
        "name": new_booking.name,
        "email": new_booking.email,
        "date": new_booking.date,
        "time": new_booking.time,
        "message": "Booking created successfully",
    }