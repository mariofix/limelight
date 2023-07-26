from flask import current_app
from flask_http_middleware import BaseHTTPMiddleware
from werkzeug.exceptions import BadRequest


class AllowedDomainsMiddleware(BaseHTTPMiddleware):
    def __init__(self):
        super().__init__()

    def dispatch(self, request, call_next):
        host = request.host.split(":")[0] if ":" in request.host else request.host
        if host not in current_app.config["ALLOWED_DOMAINS"]:
            raise BadRequest(f"{host} not in ALLOWED_DOMAINS")
        return call_next(request)
