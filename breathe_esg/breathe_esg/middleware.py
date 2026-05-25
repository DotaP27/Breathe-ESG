from django.utils.deprecation import MiddlewareMixin


class DevCorsMiddleware(MiddlewareMixin):
    """Very small CORS middleware for development only.

    Adds permissive CORS headers so the Vite dev server can call the API during local development.
    Do NOT use in production.
    """

    def process_request(self, request):
        # respond to OPTIONS preflight early
        if request.method == 'OPTIONS':
            from django.http import HttpResponse
            response = HttpResponse()
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            return response

    def process_response(self, request, response):
        response.setdefault('Access-Control-Allow-Origin', '*')
        response.setdefault('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        response.setdefault('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        return response
