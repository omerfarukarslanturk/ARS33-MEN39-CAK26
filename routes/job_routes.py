from flask import Blueprint, flash, redirect, render_template, request, url_for

from database import (
    JOB_TYPES,
    add_log,
    create_job,
    get_job,
    get_report_counts,
    list_applications_for_job,
    list_applications_for_jobseeker,
    list_jobs,
    list_jobs_by_employer,
    soft_delete_job,
    update_job,
)
from routes import current_user, login_required, role_required


job_bp = Blueprint("job", __name__)


@job_bp.context_processor
def inject_user():
    return {"current_user": current_user(), "job_types": JOB_TYPES}


@job_bp.route("/")
def index():
    jobs = list_jobs(
        keyword=request.args.get("q", "").strip(),
        sehir=request.args.get("sehir", "").strip(),
        is_turu=request.args.get("is_turu", "").strip(),
    )
    return render_template("index.html", jobs=jobs)


@job_bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    if user["user_type"] == "admin":
        return render_template("dashboard/admin.html", counts=get_report_counts())
    if user["user_type"] == "employer":
        return render_template("dashboard/employer.html", jobs=list_jobs_by_employer(user["id"]))
    applications = list_applications_for_jobseeker(user["id"])
    return render_template("dashboard/jobseeker.html", applications=applications)


@job_bp.route("/jobs")
def jobs():
    items = list_jobs(
        keyword=request.args.get("q", "").strip(),
        sehir=request.args.get("sehir", "").strip(),
        is_turu=request.args.get("is_turu", "").strip(),
    )
    return render_template("jobs/list.html", jobs=items)


@job_bp.route("/jobs/<int:job_id>")
def detail(job_id):
    job = get_job(job_id)
    if not job:
        flash("İlan bulunamadı.", "error")
        return redirect(url_for("job.jobs"))
    return render_template("jobs/detail.html", job=job)


@job_bp.route("/jobs/create", methods=["GET", "POST"])
@role_required("employer")
def create():
    if request.method == "POST":
        user = current_user()
        job_id = create_job(
            baslik=request.form.get("baslik", "").strip(),
            aciklama=request.form.get("aciklama", "").strip(),
            maas=request.form.get("maas", "").strip(),
            sehir=request.form.get("sehir", "").strip(),
            is_turu=request.form.get("is_turu", "tam_zamanli"),
            employer_id=user["id"],
        )
        add_log(user["id"], "ilan_olusturma", f"İlan oluşturuldu: #{job_id}")
        flash("İlan başarıyla oluşturuldu.", "success")
        return redirect(url_for("job.dashboard"))
    return render_template("jobs/create.html", job=None)


@job_bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@role_required("employer")
def edit(job_id):
    user = current_user()
    job = get_job(job_id)
    if not job or job["employer_id"] != user["id"]:
        flash("İlan bulunamadı veya yetkiniz yok.", "error")
        return redirect(url_for("job.dashboard"))

    if request.method == "POST":
        update_job(job_id, user["id"], request.form)
        add_log(user["id"], "ilan_duzenleme", f"İlan güncellendi: #{job_id}")
        flash("İlan güncellendi.", "success")
        return redirect(url_for("job.dashboard"))

    return render_template("jobs/create.html", job=job)


@job_bp.route("/jobs/<int:job_id>/delete", methods=["POST"])
@role_required("employer")
def delete(job_id):
    user = current_user()
    soft_delete_job(job_id, user["id"])
    add_log(user["id"], "ilan_silme", f"İlan pasifleştirildi: #{job_id}")
    flash("İlan pasifleştirildi.", "success")
    return redirect(url_for("job.dashboard"))


@job_bp.route("/jobs/<int:job_id>/applicants")
@role_required("employer")
def applicants(job_id):
    user = current_user()
    return render_template(
        "jobs/applicants.html",
        job=get_job(job_id),
        applications=list_applications_for_job(job_id, user["id"]),
    )
