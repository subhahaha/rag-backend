from pydantic import BaseModel


class BookingCreate(BaseModel):
    name: str
    email: str
    date: str
    time: str