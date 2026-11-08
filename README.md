# To-do uygulaması (FastAPI + SQLite + JavaScript)

Görev ekleme, tamamlandı olarak işaretleme, düzenleme (çift tık), silme ve filtreleme yapan basit bir web uygulaması.
Backend Python/FastAPI ile yazıldı, veriler SQLite veritabanında (`todos.db`) tutuluyor. Frontend düz HTML, CSS ve JavaScript.

## Klasör yapısı

```
todo-app/
├── main.py            # backend: API ve veritabanı
├── requirements.txt   # gerekli Python paketleri
├── .gitignore         # GitHub'a yüklenmeyecek dosyalar
└── static/
    ├── index.html     # sayfa iskeleti
    ├── style.css      # görünüm
    └── app.js         # API'yi çağıran ve listeyi çizen kod
```

## Bilgisayarında çalıştırma (Windows)

1. Python 3.10 veya üstü kurulu olmalı. Terminalde `python --version` yaz. Yoksa python.org'dan indir ve kurulumda **Add python.exe to PATH** kutusunu işaretle.
2. `todo-app` klasörünü VS Code ile aç (**File → Open Folder**).
3. VS Code'da **Terminal → New Terminal** aç ve sırayla yaz:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
fastapi dev main.py
```

4. Tarayıcıda aç:
   - Uygulama: http://127.0.0.1:8000
   - API test sayfası: http://127.0.0.1:8000/docs

Durdurmak için terminalde **Ctrl+C**. Sonraki seferlerde sadece `.venv\Scripts\activate` ve `fastapi dev main.py` yeterli.

`activate` komutu "running scripts is disabled" hatası verirse bir kere şunu çalıştır, sonra tekrar dene:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## API

| Metot | Adres | Ne yapar |
| --- | --- | --- |
| GET | `/api/todos` | Tüm görevleri listeler |
| POST | `/api/todos` | Yeni görev ekler. Gövde: `{"title": "Süt al"}` |
| PATCH | `/api/todos/{id}` | Görevi günceller. Gövde: `{"done": true}` veya `{"title": "..."}` |
| DELETE | `/api/todos/{id}` | Görevi siler |

## Kendini geliştirmek için ek görevler

1. Görevlere son tarih (`due_date`) alanı ekle ve geciken görevleri kırmızı göster.
2. "Tamamlananları temizle" düğmesi ekle (yeni bir `DELETE /api/todos?done=true` uç noktası gerekir).
3. `pytest` ile API için test yaz (FastAPI'nin `TestClient`'ı ile).
4. Görevleri sürükle bırak ile sıralanabilir yap.
