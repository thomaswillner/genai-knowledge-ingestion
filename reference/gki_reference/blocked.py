"""Fail-closed error type carrying the spec's normative BLOCKED reason codes."""


class Blocked(Exception):
    """Raised whenever a gate cannot meet its contract. Never swallowed.

    code must be one of the normative reason codes defined in the canonical
    specification (see docs/FAILURE-CODES.md for the full table).
    """

    def __init__(self, code: str, detail: str = ""):
        self.code = code
        self.detail = detail
        super().__init__(f"BLOCKED: {code}" + (f" — {detail}" if detail else ""))
