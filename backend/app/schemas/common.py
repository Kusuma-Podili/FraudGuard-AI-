"""Common Pydantic Schemas, Pagination, and API Responses."""

from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standardized API response wrapper."""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None
    timestamp: datetime = datetime.utcnow()

    model_config = ConfigDict(arbitrary_types_allowed=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated collection payload."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)
