from django.http import HttpResponseRedirect


def redirect_to_admin_for_unauthenticated(func):
    def wrapper(*args, **kwargs):
        if len(args) < 1:
            raise RuntimeError("Expecting request parameter at position 0")

        request = args[0]
        if not request.user.is_authenticated:
            return HttpResponseRedirect('admin')

        return func(*args, **kwargs)

    return wrapper
