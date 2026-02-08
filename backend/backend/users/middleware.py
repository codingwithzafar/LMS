from django.utils import timezone


class UpdateLastSeenMiddleware:
    """Update request.user.last_seen for simple online indicator.

    ✅ Purpose: teacher chatda student online/offline ko'rsin.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            try:
                user.last_seen = timezone.now()
                user.save(update_fields=["last_seen"])
            except Exception:
                # Do not break request on save errors
                pass
        return response
