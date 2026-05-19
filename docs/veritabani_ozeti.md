# Veritabanı Özeti

Projede SQLite kullanılmıştır. Veritabanı uygulama ilk çalıştığında otomatik olarak oluşturulur.

## Veritabanı Dosyası

```text
src/job_platform/data/job_platform.db
```

Bu dosya SQLite veritabanı dosyasıdır ve VS Code içinde düz metin gibi açılmaz. Tabloları görüntülemek için SQLite Viewer veya DB Browser for SQLite kullanılabilir.

## Tablolar

### users

Kullanıcı bilgilerini tutar. İş arayan, işveren ve admin rolleri bu tabloda saklanır.

### jobs

İş ilanlarını tutar. Her ilanın bir işveren kullanıcısı vardır.

### applications

İş arayanların ilanlara yaptığı başvuruları tutar. Ön yazı alanı da bu tabloda saklanır.

### logs

Giriş, çıkış, ilan oluşturma ve başvuru gibi sistem hareketlerini tutar.

## İlişkiler

- `jobs.employer_id` -> `users.id`
- `applications.job_id` -> `jobs.id`
- `applications.jobseeker_id` -> `users.id`
- `logs.user_id` -> `users.id`
