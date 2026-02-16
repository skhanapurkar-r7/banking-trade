"""Database connection and table definitions."""

from typing import Generator

from sqlalchemy import Boolean, Column, Date, Index, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool

from app.core.config import settings
from app.core.datetime_utils import get_current_date_utc

# Connection pool configuration
# For SQLite: Use StaticPool (single connection) or NullPool
# For PostgreSQL/MySQL: Use QueuePool with connection limits

if "sqlite" in settings.database_url:
    # SQLite: Use StaticPool for single-threaded access
    # Note: SQLite doesn't benefit from connection pooling in the same way
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Set to True for SQL query logging
    )
else:
    # PostgreSQL/MySQL: Use QueuePool with connection limits
    engine = create_engine(
        settings.database_url,
        poolclass=QueuePool,
        pool_size=10,  # Number of connections to maintain in the pool
        max_overflow=20,  # Additional connections that can be created on demand
        pool_timeout=30,  # Seconds to wait before giving up on getting a connection
        pool_recycle=3600,  # Recycle connections after 1 hour (prevents stale connections)
        pool_pre_ping=True,  # Verify connections before using them
        echo=False,  # Set to True for SQL query logging
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


class TradeDB(Base):
    """SQLAlchemy model for trades table."""

    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String(50), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    counter_party_id = Column(String(50), nullable=False)
    book_id = Column(String(50), nullable=False, index=True)
    maturity_date = Column(Date, nullable=False)
    created_date = Column(Date, nullable=False, default=get_current_date_utc)
    expired = Column(Boolean, nullable=False, default=False, index=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)

    __table_args__ = (
        # Composite index for version conflict checks and lookups
        Index("idx_trade_id_version", "trade_id", "version"),
        # Composite index for expired trade updates
        Index("idx_maturity_expired", "maturity_date", "expired"),
    )


def init_db() -> None:
    """
    Initialize database by creating all tables.

    Creates all tables defined in Base metadata if they don't exist.
    """
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Yields:
        Session: SQLAlchemy database session

    Usage:
        Used as FastAPI dependency for route handlers

    Note:
        Connection is automatically returned to pool when session closes
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_pool_status() -> dict:
    """
    Get current connection pool status for monitoring.

    Returns:
        dict: Pool statistics including size, checked out connections, etc.
    """
    pool = engine.pool

    # StaticPool doesn't have size() method, handle gracefully
    try:
        return {
            "pool_size": pool.size(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow(),
        }
    except AttributeError:
        # StaticPool or other pool types without these methods
        return {
            "pool_type": pool.__class__.__name__,
            "message": "Pool statistics not available for this pool type",
        }
