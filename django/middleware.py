import time
from django.db import connections

class DatabaseFallbackMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the default database is available
        try:
            connections['default'].ensure_connection()
        except Exception as e:
            # If the connection fails, wait for 1 minute and switch to a fallback database
            time.sleep(60)
            connections['default'].close()
            connections['default'] = connections['fallback']
        
        response = self.get_response(request)
        return response
