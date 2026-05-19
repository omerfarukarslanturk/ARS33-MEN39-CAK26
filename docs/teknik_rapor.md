# Teknik Rapor

## Genel Mimari

Proje Flask tabanlı modüler bir web uygulamasıdır. Uygulama `main.py` üzerinden başlatılır. Asıl proje kodları `src/job_platform/` klasörü altında bulunur.

## Ana Dosyalar

- `app.py`: Flask uygulamasını oluşturur ve blueprint yapılarını kaydeder.
- `database.py`: SQLite bağlantısı, tablo oluşturma ve veritabanı işlemlerini yönetir.
- `models.py`: Nesne yönelimli sınıf yapılarını içerir.
- `routes/`: Kullanıcı, ilan, başvuru, admin ve profil rotalarını içerir.
- `templates/`: HTML/Jinja şablonlarını içerir.
- `static/`: CSS ve JavaScript dosyalarını içerir.

## Çalışma Mantığı

Kullanıcı web arayüzünden işlem yapar. Flask rotaları bu isteği karşılar. Veritabanı işlemleri `database.py` üzerinden SQLite ile yapılır. Sonuçlar Jinja şablonları aracılığıyla HTML sayfalarında gösterilir.
