from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv(
	"DATABASE_URL",
	# e.g., mysql+pymysql://user:pass@localhost:3306/sih
	"sqlite:///./dev.db",
)

engine = create_engine(
	DATABASE_URL,
	pool_pre_ping=True,
	future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def get_db():
	from sqlalchemy.orm import Session
	db: Session = SessionLocal()
	try:
		yield db
	finally:
		db.close()
