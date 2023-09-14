from typing import Tuple

from sqlalchemy.orm import Session

from . import models, schemas

import datetime


class UnableToBook(Exception):
    pass


class CannotExtendStay(Exception):
    pass


def create_booking(db: Session, booking: schemas.BookingBase) -> models.Booking:
    (is_possible, reason) = is_booking_possible(db=db, booking=booking)
    if not is_possible:
        raise UnableToBook(reason)

    check_out_date = booking.check_in_date + datetime.timedelta(
        days=booking.number_of_nights
    )
    db_booking = models.Booking(
        guest_name=booking.guest_name,
        unit_id=booking.unit_id,
        check_in_date=booking.check_in_date,
        check_out_date=check_out_date,
        number_of_nights=booking.number_of_nights,
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def update_booking(db: Session, booking: schemas.BookingBase):
    is_update = is_update_possible(
        db=db,
        unit_id=booking.unit_id,
        guest_name=booking.guest_name,
        number_of_nights=booking.number_of_nights,
    )
    if is_update:
        raise CannotExtendStay(
            "Your stay in this unit cannot be extended. Recommend booking another unit"
        )

    user_data = (
        db.query(models.Booking).filter_by(guest_name=booking.guest_name).first()
    )
    check_out_date = user_data.check_out_date + datetime.timedelta(
        days=booking.number_of_nights
    )
    user_data.number_of_nights += booking.number_of_nights
    user_data.check_out_date = check_out_date
    db.commit()
    return {"message": "user data updated successfully"}


def is_booking_possible(db: Session, booking: schemas.BookingBase) -> Tuple[bool, str]:
    # check 1 : The Same guest cannot book the same unit multiple times
    is_same_guest_booking_same_unit = (
        db.query(models.Booking)
        .filter_by(guest_name=booking.guest_name, unit_id=booking.unit_id)
        .first()
    )

    if is_same_guest_booking_same_unit:
        return False, "The given guest name cannot book the same unit multiple times"

    # check 2 : the same guest cannot be in multiple units at the same time
    is_same_guest_already_booked = (
        db.query(models.Booking).filter_by(guest_name=booking.guest_name).first()
    )
    if is_same_guest_already_booked:
        return False, "The same guest cannot be in multiple units at the same time"

    # check 3 : Unit is available for the check-in date
    is_unit_available_on_check_in_date = (
        db.query(models.Booking).filter_by(unit_id=booking.unit_id).first()
    )

    if is_unit_available_on_check_in_date:
        if (
            booking.check_in_date >= is_unit_available_on_check_in_date.check_in_date
            and booking.check_in_date
            <= is_unit_available_on_check_in_date.check_out_date
        ):
            return False, "For the given check-in date, the unit is already occupied"

    return True, "OK"


def is_update_possible(
    db: Session, guest_name: str, unit_id: str, number_of_nights: int
):
    result_set = db.query(models.Booking).filter_by(unit_id=unit_id).all()
    if len(result_set) <= 1:
        return False

    for index in range(len(result_set)):
        if result_set[index].guest_name == guest_name and (index + 1) < len(result_set):
            date_diff = (
                result_set[index + 1].check_in_date - result_set[index].check_out_date
            )

            if date_diff.days < number_of_nights:
                return True
        else:
            return False

    return True
