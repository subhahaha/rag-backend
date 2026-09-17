from sqlalchemy.orm import Session

from models import Booking
from app.schemas.booking import BookingCreate


def create_booking(
    db: Session,
    booking: BookingCreate,
) -> Booking:
    new_booking = Booking(
        name=booking.name,
        email=booking.email,
        date=booking.date,
        time=booking.time,
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking