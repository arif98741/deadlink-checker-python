from dataclasses import dataclass
from typing import Optional

@dataclass
class LinkResult:
    """Stores the result of checking a link."""
    url: str
    status_code: Optional[int]
    status_text: str
    response_time: Optional[float]
    found_on: str
    is_dead: bool
    is_external: bool
    link_type: str = "Link"
