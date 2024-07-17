# views.py
from nebula.utils import HTTPResponse


class APIView:
    def dispatch(self, request, *args, **kwargs):
        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        return handler(request, *args, **kwargs)

    @staticmethod
    def http_method_not_allowed(request, *args, **kwargs):
        return HTTPResponse("Method not allowed", 405)


def as_view(self):
    def view(request, *args, **kwargs):
        self_instance = self()
        return self_instance.dispatch(request, *args, **kwargs)
    return view


APIView.as_view = classmethod(as_view)
