import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./infrasense.db"
)

if SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_timescaledb(db):
    """Initialize TimescaleDB extensions and hypertable."""
    if not SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
        return
    
    try:
        db.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
        db.execute(text("""
            SELECT create_hypertable('component_metrics', 'timestamp', 
            if_not_exists => TRUE)
        """))
        db.execute(text("""
            ALTER TABLE component_metrics SET (
                timescaledb.compress,
                timescaledb.compress_segmentby = 'component_id, metric_name'
            )
        """))
        db.execute(text("""
            SELECT add_compression_policy('component_metrics', INTERVAL '7 days')
        """))
        db.commit()
    except Exception as e:
        print(f"TimescaleDB init: {e}")
        db.rollback()