from functools import wraps

from flask import flash, redirect, session, url_for

from database import get_user_by_id


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user():
            flash("Devam etmek için giriş yapmalısınız.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapper


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = current_user()
            if not user:
                flash("Devam etmek için giriş yapmalısınız.", "error")
                return redirect(url_for("auth.login"))
            if user["user_type"] not in roles:
                flash("Bu sayfaya erişim yetkiniz yok.", "error")
                return redirect(url_for("job.index"))
            return view(*args, **kwargs)

        return wrapper

    return decorator
