from datetime import date, datetime, time
from decimal import Decimal


def json_serializer(obj):
    """Handle types that json.dumps can't serialize by default."""
    if isinstance(obj, datetime):
        return obj.date().isoformat()
    if isinstance(obj, (date, time)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        # Return an INTEGER type no matter what the database result is, as AVG() would return a DECIMAL
        return int(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
