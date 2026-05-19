from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database import add_log, create_user, get_user_by_email
from routes import current_user


auth_bp = Blueprint("auth", __name__)


@auth_bp.context_processor
def inject_user():
    return {"current_user": current_user()}


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_user_by_email(email)

        if not user or not check_password_hash(user["password_hash"], password):
            flash("E-posta veya şifre hatalı.", "error")
            return render_template("login.html")
        if not user["active"]:
            flash("Bu hesap deaktive edilmiş.", "error")
            return render_template("login.html")

        session["user_id"] = user["id"]
        add_log(user["id"], "giris", "Kullanıcı giriş yaptı.")
        flash("Başarıyla giriş yaptınız.", "success")
        return redirect(url_for("job.dashboard"))

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_type = request.form.get("user_type", "jobseeker")
        email = request.form.get("email", "").strip().lower()

        if user_type not in ("jobseeker", "employer"):
            flash("Geçersiz kullanıcı tipi.", "error")
            return render_template("register.html")
        if get_user_by_email(email):
            flash("Bu e-posta adresi zaten kayıtlı.", "error")
            return render_template("register.html")

        user_id = create_user(
            username=request.form.get("username", "").strip(),
            email=email,
            password=request.form.get("password", ""),
            user_type=user_type,
            sehir=request.form.get("sehir", "").strip(),
            sirket_adi=request.form.get("sirket_adi", "").strip(),
        )
        add_log(user_id, "kayit", "Yeni kullanıcı kaydoldu.")
        flash("Kayıt başarılı. Giriş yapabilirsiniz.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    user_id = session.get("user_id")
    if user_id:
        add_log(user_id, "cikis", "Kullanıcı çıkış yaptı.")
    session.clear()
    flash("Çıkış yaptınız.", "success")
    return redirect(url_for("job.index"))
