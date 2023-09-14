from http import HTTPStatus

from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .crud import UnableToBook, CannotExtendStay
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def hello_world():
    return {"message": "OK"}


@app.post("/api/v1/booking", response_model=schemas.BookingBase)
def create_booking(booking: schemas.BookingBase, db: Session = Depends(get_db)):
    try:
        return crud.create_booking(db=db, booking=booking)
    except UnableToBook as unable_to_book:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=str(unable_to_book)
        )


@app.put("/api/v1/booking/update")
def extend_booking(booking: schemas.BookingBase, db: Session = Depends(get_db)):
    try:
        return crud.update_booking(db=db, booking=booking)
    except CannotExtendStay as cannot_extend_stay:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=str(cannot_extend_stay)
        )
