# Adapted from http://stackoverflow.com/a/11525851/1777162
from django.utils.decorators import method_decorator
from inspect import isfunction

def patched_decorator(dec, obj):
    """
    Takes an argument-less decorator and an object which can be either a
    function or a class based view.

    If `obj` is a function, returns the function decorated with `dec`.
    
    If `obj` is a CBV, returns the class with its dispatch method decorated
    with `dec`.
    """
    if isfunction(obj):
        return dec(obj)
    else:
        cls = obj
        cls.dispatch = method_decorator(dec)(cls.dispatch)
        return cls

def patch_view_decorator(dec):
    """
    Takes a decorator and returns a 'patched' version of it which works both
    with function views and CBV.
    """
    return lambda obj: patched_decorator(dec, obj)

def patch_view_decorator_with_args(dec):
    """
    Takes a decorator which requires arguments and returns a 'patched' version
    of it which works both with function views and CBV.
    """
    def _patched_decorator(*args, **kwargs):
        return lambda obj: patched_decorator(dec(*args, **kwargs), obj)
    return _patched_decorator


from django.contrib.auth.decorators import login_required, permission_required 

login_required = patch_view_decorator(login_required)
permission_required = patch_view_decorator_with_args(permission_required)

@patch_view_decorator
def ajax_view(view):
    def _inner(request, *args, **kwargs):
        if request.is_ajax():
            return view(request, *args, **kwargs)
        else:
            raise Http404

    return _inner
