from sqlalchemy import Column, Integer, String, Date

from .database import Base


class Booking(Base):
    __tablename__ = "booking"

    id = Column(Integer, primary_key=True, index=True)
    guest_name = Column(String)
    unit_id = Column(String)
    check_in_date = Column(Date)
    check_out_date = Column(Date)
    number_of_nights = Column(Integer)
