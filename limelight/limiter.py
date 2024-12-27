from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    get_remote_address,
    storage_uri="memory://",
    # storage_uri="redis://localhost:6379",
    strategy="fixed-window",
)
