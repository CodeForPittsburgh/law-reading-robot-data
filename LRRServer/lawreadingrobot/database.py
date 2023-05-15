import os

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine: Engine = create_engine(os.environ["SQLALCHEMY_DATABASE_URI"])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
metadata = Base.metadata
Base.metadata.create_all(bind=engine)
