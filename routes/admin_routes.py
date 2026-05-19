from flask import Blueprint, flash, redirect, render_template, url_for

from database import add_log, deactivate_user, get_all_users, get_logs, get_report_counts, list_jobs
from routes import current_user, role_required


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.context_processor
def inject_user():
    return {"current_user": current_user()}


@admin_bp.route("/users")
@role_required("admin")
def users():
    return render_template("admin/users.html", users=get_all_users())


@admin_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
@role_required("admin")
def deactivate(user_id):
    admin = current_user()
    if user_id == admin["id"]:
        flash("Kendi admin hesabınızı deaktive edemezsiniz.", "error")
    else:
        deactivate_user(user_id)
        add_log(admin["id"], "kullanici_deaktive", f"Kullanıcı deaktive edildi: #{user_id}")
        flash("Kullanıcı deaktive edildi.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/logs")
@role_required("admin")
def logs():
    return render_template("admin/logs.html", logs=get_logs())


@admin_bp.route("/reports")
@role_required("admin")
def reports():
    return render_template("admin/reports.html", counts=get_report_counts(), jobs=list_jobs(include_inactive=True))
