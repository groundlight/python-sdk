"""Models for the authenticated caller returned by Groundlight.me()."""

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class Group(BaseModel):  # pylint: disable=too-few-public-methods
    """A Groundlight customer group (tenant) the authenticated user belongs to."""

    model_config = ConfigDict(extra="ignore")

    id: int = Field(..., description="Numeric id of the customer group.")
    name: str = Field(..., description="Name of the customer group.")


class Me(BaseModel):  # pylint: disable=too-few-public-methods
    """Identity information for the authenticated API token from GET /v1/me."""

    model_config = ConfigDict(extra="ignore")

    id: int = Field(..., description="Numeric id of the authenticated user.")
    email: str = Field(..., description="Email address of the authenticated user.")
    username: str = Field(..., description="Username of the authenticated user.")
    groups: List[Group] = Field(
        ...,
        description="Customer groups the authenticated user belongs to.",
    )
