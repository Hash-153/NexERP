"""
NexERP Generic Pagination and Sorting Subsystem.
Standardizes paginated API responses across all enterprise list endpoints.
"""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for pagination and sorting."""
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=200, description="Number of items per page")
    sort_by: Optional[str] = Field(default="created_at", description="Field name to sort by")
    sort_order: Optional[str] = Field(default="desc", description="Sort direction: 'asc' or 'desc'")
    search: Optional[str] = Field(default=None, description="Free-text search query")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard generic wrapper for all paginated JSON collections."""
    items: List[T]
    total_items: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def create(cls, items: List[T], total_items: int, params: PaginationParams) -> "PaginatedResponse[T]":
        total_pages = (total_items + params.page_size - 1) // params.page_size if params.page_size > 0 else 1
        return cls(
            items=items,
            total_items=total_items,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_previous=params.page > 1
        )
