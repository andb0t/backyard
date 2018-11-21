from uuid import UUID


def is_uuid(value):
    """check if value is a valid UUID (v4)"""
    try:
        UUID(value, version=4)
    except ValueError:
        return False

    return True
