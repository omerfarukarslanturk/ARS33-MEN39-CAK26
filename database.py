import os
import sqlite3
from datetime import datetime

from werkzeug.security import generate_password_hash


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "job_platform.db")

JOB_TYPES = ("tam_zamanli", "yari_zamanli", "uzaktan", "staj")
APPLICATION_STATUSES = ("beklemede", "incelendi", "kabul_edildi", "reddedildi")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def execute(query, params=(), commit=True):
    with get_connection() as conn:
        cursor = conn.execute(query, params)
        if commit:
            conn.commit()
        return cursor.lastrowid


def fetch_one(query, params=()):
    with get_connection() as conn:
        return conn.execute(query, params).fetchone()


def fetch_all(query, params=()):
    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def init_db():
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "outputs"), exist_ok=True)

    schema = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            user_type TEXT NOT NULL CHECK(user_type IN ('jobseeker', 'employer', 'admin')),
            bio TEXT DEFAULT '',
            beceriler TEXT DEFAULT '',
            sehir TEXT DEFAULT '',
            ozgecmis_metni TEXT DEFAULT '',
            sirket_adi TEXT DEFAULT '',
            sirket_aciklamasi TEXT DEFAULT '',
            website TEXT DEFAULT '',
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            baslik TEXT NOT NULL,
            aciklama TEXT NOT NULL,
            maas TEXT DEFAULT '',
            sehir TEXT NOT NULL,
            is_turu TEXT NOT NULL CHECK(is_turu IN ('tam_zamanli', 'yari_zamanli', 'uzaktan', 'staj')),
            employer_id INTEGER NOT NULL,
            olusturulma_tarihi TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            aktif_mi INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (employer_id) REFERENCES users(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            jobseeker_id INTEGER NOT NULL,
            on_yazi TEXT DEFAULT '',
            durum TEXT NOT NULL DEFAULT 'beklemede'
                CHECK(durum IN ('beklemede', 'incelendi', 'kabul_edildi', 'reddedildi')),
            basvuru_tarihi TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(job_id, jobseeker_id),
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (jobseeker_id) REFERENCES users(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            islem TEXT NOT NULL,
            zaman TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            detay TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """,
    ]

    with get_connection() as conn:
        for statement in schema:
            conn.execute(statement)
        columns = conn.execute("PRAGMA table_info(applications)").fetchall()
        column_names = {column["name"] for column in columns}
        if "on_yazi" not in column_names:
            conn.execute("ALTER TABLE applications ADD COLUMN on_yazi TEXT DEFAULT ''")
        conn.commit()

    seed_demo_data()


def seed_demo_data():
    demo_users = [
        {
            "username": "Admin",
            "email": "admin@jobplatform.com",
            "password": "admin123",
            "user_type": "admin",
        },
        {
            "username": "Tech AS",
            "email": "isveren@test.com",
            "password": "test123",
            "user_type": "employer",
            "sirket_adi": "Tech A.Ş.",
            "sirket_aciklamasi": "Yazılım ve teknoloji çözümleri geliştiren demo şirket.",
            "website": "https://tech-as.example",
        },
        {
            "username": "Demo Is Arayan",
            "email": "isarayan@test.com",
            "password": "test123",
            "user_type": "jobseeker",
            "bio": "Frontend ve Flask projelerine ilgi duyan iş arayan.",
            "beceriler": "Python, Flask, JavaScript, HTML, CSS",
            "sehir": "Istanbul",
            "ozgecmis_metni": "Demo özgeçmiş metni.",
        },
    ]

    for user in demo_users:
        if not get_user_by_email(user["email"]):
            create_user(
                username=user["username"],
                email=user["email"],
                password=user["password"],
                user_type=user["user_type"],
                bio=user.get("bio", ""),
                beceriler=user.get("beceriler", ""),
                sehir=user.get("sehir", ""),
                ozgecmis_metni=user.get("ozgecmis_metni", ""),
                sirket_adi=user.get("sirket_adi", ""),
                sirket_aciklamasi=user.get("sirket_aciklamasi", ""),
                website=user.get("website", ""),
            )

    employer = get_user_by_email("isveren@test.com")
    if employer and not fetch_one("SELECT id FROM jobs WHERE employer_id = ?", (employer["id"],)):
        create_job(
            baslik="Junior Flask Developer",
            aciklama="Flask, SQLite ve modern web arayüzleriyle çalışacak ekip arkadaşı arıyoruz.",
            maas="35.000 - 50.000 TL",
            sehir="Istanbul",
            is_turu="tam_zamanli",
            employer_id=employer["id"],
        )
        create_job(
            baslik="Uzaktan Frontend Stajyeri",
            aciklama="HTML, CSS ve JavaScript öğrenmeye açık stajyer takım arkadaşı.",
            maas="Staj ücreti",
            sehir="Remote",
            is_turu="staj",
            employer_id=employer["id"],
        )


def create_user(**data):
    password_hash = generate_password_hash(data["password"])
    return execute(
        """
        INSERT INTO users (
            username, email, password_hash, user_type, bio, beceriler, sehir,
            ozgecmis_metni, sirket_adi, sirket_aciklamasi, website
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["username"],
            data["email"].lower(),
            password_hash,
            data["user_type"],
            data.get("bio", ""),
            data.get("beceriler", ""),
            data.get("sehir", ""),
            data.get("ozgecmis_metni", ""),
            data.get("sirket_adi", ""),
            data.get("sirket_aciklamasi", ""),
            data.get("website", ""),
        ),
    )


def get_user_by_email(email):
    return fetch_one("SELECT * FROM users WHERE email = ?", (email.lower(),))


def get_user_by_id(user_id):
    return fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))


def get_all_users():
    return fetch_all("SELECT * FROM users ORDER BY created_at DESC")


def update_user_profile(user_id, data):
    execute(
        """
        UPDATE users
        SET username = ?, bio = ?, beceriler = ?, sehir = ?, ozgecmis_metni = ?,
            sirket_adi = ?, sirket_aciklamasi = ?, website = ?
        WHERE id = ?
        """,
        (
            data.get("username", ""),
            data.get("bio", ""),
            data.get("beceriler", ""),
            data.get("sehir", ""),
            data.get("ozgecmis_metni", ""),
            data.get("sirket_adi", ""),
            data.get("sirket_aciklamasi", ""),
            data.get("website", ""),
            user_id,
        ),
    )


def deactivate_user(user_id):
    execute("UPDATE users SET active = 0 WHERE id = ?", (user_id,))


def create_job(baslik, aciklama, maas, sehir, is_turu, employer_id):
    return execute(
        """
        INSERT INTO jobs (baslik, aciklama, maas, sehir, is_turu, employer_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (baslik, aciklama, maas, sehir, is_turu, employer_id),
    )


def update_job(job_id, employer_id, data):
    execute(
        """
        UPDATE jobs
        SET baslik = ?, aciklama = ?, maas = ?, sehir = ?, is_turu = ?
        WHERE id = ? AND employer_id = ?
        """,
        (
            data["baslik"],
            data["aciklama"],
            data.get("maas", ""),
            data["sehir"],
            data["is_turu"],
            job_id,
            employer_id,
        ),
    )


def soft_delete_job(job_id, employer_id=None):
    if employer_id:
        execute("UPDATE jobs SET aktif_mi = 0 WHERE id = ? AND employer_id = ?", (job_id, employer_id))
    else:
        execute("UPDATE jobs SET aktif_mi = 0 WHERE id = ?", (job_id,))


def get_job(job_id):
    return fetch_one(
        """
        SELECT jobs.*, users.sirket_adi, users.username AS employer_name
        FROM jobs
        JOIN users ON users.id = jobs.employer_id
        WHERE jobs.id = ?
        """,
        (job_id,),
    )


def list_jobs(keyword="", sehir="", is_turu="", include_inactive=False):
    query = """
        SELECT jobs.*, users.sirket_adi, users.username AS employer_name
        FROM jobs
        JOIN users ON users.id = jobs.employer_id
        WHERE (? = 1 OR jobs.aktif_mi = 1)
          AND (? = '' OR LOWER(jobs.baslik) LIKE LOWER(?))
          AND (? = '' OR LOWER(jobs.sehir) LIKE LOWER(?))
          AND (? = '' OR jobs.is_turu = ?)
        ORDER BY jobs.olusturulma_tarihi DESC
    """
    keyword_like = f"%{keyword}%"
    city_like = f"%{sehir}%"
    return fetch_all(query, (1 if include_inactive else 0, keyword, keyword_like, sehir, city_like, is_turu, is_turu))


def list_jobs_by_employer(employer_id):
    return fetch_all(
        """
        SELECT jobs.*, COUNT(applications.id) AS basvuru_sayisi
        FROM jobs
        LEFT JOIN applications ON applications.job_id = jobs.id
        WHERE jobs.employer_id = ?
        GROUP BY jobs.id
        ORDER BY jobs.olusturulma_tarihi DESC
        """,
        (employer_id,),
    )


def create_application(job_id, jobseeker_id, on_yazi=""):
    return execute(
        "INSERT INTO applications (job_id, jobseeker_id, on_yazi) VALUES (?, ?, ?)",
        (job_id, jobseeker_id, on_yazi),
    )


def has_application(job_id, jobseeker_id):
    return fetch_one(
        "SELECT id FROM applications WHERE job_id = ? AND jobseeker_id = ?",
        (job_id, jobseeker_id),
    )


def list_applications_for_job(job_id, employer_id):
    return fetch_all(
        """
        SELECT applications.*, users.username, users.email, users.beceriler, users.sehir
        FROM applications
        JOIN jobs ON jobs.id = applications.job_id
        JOIN users ON users.id = applications.jobseeker_id
        WHERE applications.job_id = ? AND jobs.employer_id = ?
        ORDER BY applications.basvuru_tarihi DESC
        """,
        (job_id, employer_id),
    )


def list_applications_for_jobseeker(jobseeker_id):
    return fetch_all(
        """
        SELECT applications.*, jobs.baslik, jobs.sehir, jobs.is_turu, users.sirket_adi
        FROM applications
        JOIN jobs ON jobs.id = applications.job_id
        JOIN users ON users.id = jobs.employer_id
        WHERE applications.jobseeker_id = ?
        ORDER BY applications.basvuru_tarihi DESC
        """,
        (jobseeker_id,),
    )


def update_application_status(application_id, employer_id, durum):
    execute(
        """
        UPDATE applications
        SET durum = ?
        WHERE id = ?
          AND job_id IN (SELECT id FROM jobs WHERE employer_id = ?)
        """,
        (durum, application_id, employer_id),
    )


def add_log(user_id, islem, detay=""):
    execute(
        "INSERT INTO logs (user_id, islem, zaman, detay) VALUES (?, ?, ?, ?)",
        (user_id, islem, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), detay),
    )


def get_logs():
    return fetch_all(
        """
        SELECT logs.*, users.email, users.username
        FROM logs
        LEFT JOIN users ON users.id = logs.user_id
        ORDER BY logs.zaman DESC
        LIMIT 250
        """
    )


def get_report_counts():
    users = fetch_one("SELECT COUNT(*) AS total FROM users")["total"]
    jobs = fetch_one("SELECT COUNT(*) AS total FROM jobs")["total"]
    applications = fetch_one("SELECT COUNT(*) AS total FROM applications")["total"]
    active_jobs = fetch_one("SELECT COUNT(*) AS total FROM jobs WHERE aktif_mi = 1")["total"]
    return {
        "users": users,
        "jobs": jobs,
        "applications": applications,
        "active_jobs": active_jobs,
    }
