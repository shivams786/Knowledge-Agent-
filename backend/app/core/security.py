from enum import IntEnum


class AccessRank(IntEnum):
    public = 1
    internal = 2
    restricted = 3


def can_access(document_access_level: str, requested_access_level: str | None) -> bool:
    """Return whether the caller's requested clearance can see a document."""

    requested = requested_access_level or "internal"
    return AccessRank[document_access_level] <= AccessRank[requested]
