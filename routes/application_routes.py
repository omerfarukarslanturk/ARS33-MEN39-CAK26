from flask import Blueprint, flash, redirect, request, url_for

from database import (
    APPLICATION_STATUSES,
    add_log,
    create_application,
    get_job,
    has_application,
    update_application_status,
)
from routes import current_user, role_required


application_bp = Blueprint("application", __name__)


@application_bp.route("/jobs/<int:job_id>/apply", methods=["POST"])
@role_required("jobseeker")
def apply(job_id):
    user = current_user()
    job = get_job(job_id)
    if not job or not job["aktif_mi"]:
        flash("Bu ilana başvuru yapılamıyor.", "error")
        return redirect(url_for("job.jobs"))
    if has_application(job_id, user["id"]):
        flash("Bu ilana zaten başvurdunuz.", "error")
        return redirect(url_for("job.detail", job_id=job_id))

    on_yazi = request.form.get("on_yazi", "").strip()
    if not on_yazi:
        flash("Başvuru yapmadan önce ön yazı eklemelisiniz.", "error")
        return redirect(url_for("job.detail", job_id=job_id))

    create_application(job_id, user["id"], on_yazi)
    add_log(user["id"], "basvuru", f"İlana başvuruldu: #{job_id}")
    flash("Başvurunuz alındı.", "success")
    return redirect(url_for("job.dashboard"))


@application_bp.route("/applications/<int:application_id>/status", methods=["POST"])
@role_required("employer")
def update_status(application_id):
    durum = request.form.get("durum", "beklemede")
    if durum not in APPLICATION_STATUSES:
        flash("Geçersiz başvuru durumu.", "error")
        return redirect(url_for("job.dashboard"))

    user = current_user()
    update_application_status(application_id, user["id"], durum)
    add_log(user["id"], "basvuru_durumu", f"Başvuru #{application_id} durumu {durum} yapıldı.")
    flash("Başvuru durumu güncellendi.", "success")
    return redirect(request.referrer or url_for("job.dashboard"))
