from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    get_remote_address,
    default_limits=["200 per day", "60 per minute"],
    storage_uri="memory://",
    strategy="fixed-window",
)
