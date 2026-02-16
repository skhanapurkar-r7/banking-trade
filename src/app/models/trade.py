"""Trade data models and schemas."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.datetime_utils import get_current_date_utc


class TradeBase(BaseModel):
    """Base trade model with common fields."""

    trade_id: str = Field(..., min_length=1, max_length=50, description="Unique trade identifier")
    version: int = Field(..., ge=1, description="Trade version number")
    counter_party_id: str = Field(
        ..., min_length=1, max_length=50, description="Counter party identifier"
    )
    book_id: str = Field(..., min_length=1, max_length=50, description="Book identifier")
    maturity_date: date = Field(..., description="Trade maturity date")

    @field_validator("maturity_date", mode="after")
    @classmethod
    def validate_maturity_date(cls, v: date) -> date:
        """
        Validate that maturity date is not in the past (UTC).

        Args:
            v: Maturity date to validate

        Returns:
            date: Validated maturity date

        Raises:
            ValueError: If maturity date is before today (UTC)
        """
        if v < get_current_date_utc():
            raise ValueError("Maturity date cannot be in the past")
        return v


class TradeCreate(TradeBase):
    """Schema for creating a new trade."""

    pass


class TradeUpdate(BaseModel):
    """Schema for updating an existing trade."""

    trade_id: str | None = Field(None, min_length=1, max_length=50, description="Unique trade identifier")
    version: int | None = Field(None, ge=1, description="Trade version number")
    counter_party_id: str | None = Field(
        None, min_length=1, max_length=50, description="Counter party identifier"
    )
    book_id: str | None = Field(None, min_length=1, max_length=50, description="Book identifier")
    maturity_date: date | None = Field(None, description="Trade maturity date")

    @field_validator("maturity_date", mode="after")
    @classmethod
    def validate_maturity_date(cls, v: date | None) -> date | None:
        """
        Validate that maturity date is not in the past (UTC).

        Args:
            v: Maturity date to validate

        Returns:
            date: Validated maturity date

        Raises:
            ValueError: If maturity date is before today (UTC)
        """
        if v is not None and v < get_current_date_utc():
            raise ValueError("Maturity date cannot be in the past")
        return v


class Trade(TradeBase):
    """Complete trade model with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Database primary key")
    created_date: date = Field(
        default_factory=get_current_date_utc, description="Trade creation date (UTC)"
    )
    expired: bool = Field(default=False, description="Whether trade has expired")
    # is_deleted is internal only, not exposed in API responses


class TradeResponse(Trade):
    """Trade response model for API responses."""

    pass


class TradeListResponse(BaseModel):
    """Paginated list of trades response."""

    trades: list[TradeResponse] = Field(default_factory=list, description="List of trades")
    total: int = Field(..., ge=0, description="Total number of trades")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
