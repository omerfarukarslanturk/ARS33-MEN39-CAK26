from flask import Blueprint, flash, redirect, render_template, request, url_for

from database import add_log, update_user_profile
from routes import current_user, login_required


profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.context_processor
def inject_user():
    return {"current_user": current_user()}


@profile_bp.route("/")
@login_required
def view():
    return render_template("profile/view.html", user=current_user())


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    user = current_user()
    if request.method == "POST":
        update_user_profile(user["id"], request.form)
        add_log(user["id"], "profil_guncelleme", "Profil bilgileri güncellendi.")
        flash("Profiliniz güncellendi.", "success")
        return redirect(url_for("profile.view"))
    return render_template("profile/edit.html", user=user)
