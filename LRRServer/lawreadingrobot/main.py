from typing import Generator, List

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency


def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/housebill/", response_model=list[schemas.HouseBillGet])
def get_housebill(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[models.HouseBill]:
    return crud.get_housebills(db, skip=skip, limit=limit)
