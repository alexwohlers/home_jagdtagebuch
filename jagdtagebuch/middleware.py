class ScriptNameMiddleware:
    """
    Middleware to handle SCRIPT_NAME for path-based routing.
    When running behind nginx at /jagdtagebuch/, this ensures
    Django generates correct URLs.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        script_name = request.META.get("HTTP_X_SCRIPT_NAME", "")
        if script_name:
            request.META["SCRIPT_NAME"] = script_name
            # Also update path info
            path_info = request.META.get("PATH_INFO", "/")
            if path_info.startswith(script_name):
                request.META["PATH_INFO"] = path_info[len(script_name):]
        return self.get_response(request)
