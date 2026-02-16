import os
from slowapi import Limiter
from slowapi.util import get_remote_address

# Disable rate limiting for tests
enabled = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
limiter = Limiter(key_func=get_remote_address, enabled=enabled)
