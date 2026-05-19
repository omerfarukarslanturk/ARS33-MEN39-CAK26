from dataclasses import dataclass


@dataclass
class User:
    id: int | None
    username: str
    email: str
    password_hash: str
    user_type: str
    created_at: str | None = None
    active: int = 1

    def giris_yap(self):
        return {"email": self.email, "user_type": self.user_type}

    def cikis_yap(self):
        return True

    def profil_getir(self):
        return self

    def profil_guncelle(self, **fields):
        for key, value in fields.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self


@dataclass
class JobSeeker(User):
    bio: str = ""
    beceriler: str = ""
    sehir: str = ""
    ozgecmis_metni: str = ""

    def ilana_basvur(self, job_id):
        return {"job_id": job_id, "jobseeker_id": self.id}

    def basvurularimi_goruntule(self):
        return []

    def is_ara(self, anahtar_kelime=""):
        return anahtar_kelime


@dataclass
class Employer(User):
    sirket_adi: str = ""
    sirket_aciklamasi: str = ""
    website: str = ""

    def ilan_olustur(self, **job_data):
        return job_data

    def ilan_duzenle(self, job_id, **job_data):
        return {"job_id": job_id, **job_data}

    def ilan_sil(self, job_id):
        return job_id

    def basvuranlari_goruntule(self, job_id):
        return job_id


@dataclass
class Admin(User):
    def tum_kullanicilari_goruntule(self):
        return []

    def tum_loglari_goruntule(self):
        return []

    def rapor_uret(self):
        return {}

    def kullanici_deaktive_et(self, user_id):
        return user_id


@dataclass
class Job:
    id: int | None
    baslik: str
    aciklama: str
    maas: str
    sehir: str
    is_turu: str
    employer_id: int
    olusturulma_tarihi: str | None = None
    aktif_mi: int = 1


@dataclass
class Application:
    id: int | None
    job_id: int
    jobseeker_id: int
    on_yazi: str = ""
    durum: str = "beklemede"
    basvuru_tarihi: str | None = None


@dataclass
class Log:
    id: int | None
    user_id: int | None
    islem: str
    zaman: str | None = None
    detay: str = ""
