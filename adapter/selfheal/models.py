from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel


@dataclass
class ErrorInfo:
    type: str  # TIMEOUT / ASSERTION
    subtype: str  # SELECTOR_NOT_FOUND
    message: str


class LocatorDescriptor(BaseModel):
    strategy: str  # text | role | css
    value: str  # "Submit", "button", etc
    role: Optional[str] = None
    attributes: Optional[str] = None
    name: Optional[str] = None  # accessible name
    exact: Optional[bool] = False
    landmark: Optional[str] = None  # form, navigation, dialog
    scope: Optional[str] = None
    options: Optional[str] = None
    rank: float = 0
    confidence: float = 0

    def to_playwright(self) -> str:
        if self.strategy == "text":
            return f'page.get_by_text("{self.value}")'

        if self.strategy == "css" or self.strategy == "xpath":
            return f'page.locator("{self.value}")'

        if self.strategy == "role":
            args = []
            if self.name:
                args.append(f', name="{self.name}"')
            if self.exact:
                args.append(f", exact={self.exact}")
            if self.options:
                args.append(self.options)  # {", " if args else ""}
            return f'page.get_by_role("{self.role}"{"".join(args)})'

        if self.strategy == "scoped_role":
            return (
                f'page.get_by_role("{self.landmark}")'
                f'.get_by_role("{self.value}", name="{self.name}")'
            )

        raise ValueError("Unsupported locator strategy")


@dataclass
class ValidationResult:
    locator: LocatorDescriptor
    locator_rank: float
    count: int
    is_unique: bool
    error: str | None = None
