from functools import wraps
from flask import g, redirect, url_for, request
from maintain_frontend import config


def requires_permission(permissions_to_check):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            authorised = False
            for permission in permissions_to_check:
                if permission in g.session.user.permissions:
                    authorised = True
            if not authorised:
                return redirect('/not-authorised')
            return func(*args, **kwargs)
        return wrapper
    return decorator


def requires_lr():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not g.session.user.is_lr():
                return redirect('/not-authorised')
            return func(*args, **kwargs)
        return wrapper
    return decorator


def requires_add_charge_session():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if g.session.add_charge_state is None:
                return redirect(url_for('add_land_charge.new'))
            return func(*args, **kwargs)
        return wrapper
    return decorator


def requires_two_factor_authentication():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if (not config.ENABLE_TWO_FACTOR_AUTHENTICATION) or g.session.two_factor_authentication_passed:
                return func(*args, **kwargs)

            g.session.two_factor_authentication_redirect_url = request.path
            g.session.commit_2fa_state()

            return redirect('/check-your-email')
        return wrapper
    return decorator
