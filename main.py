"""
To-do uygulaması: backend (FastAPI + SQLite)

Çalıştırmak için:  fastapi dev main.py
Sonra tarayıcıda:  http://127.0.0.1:8000        (uygulama)
                   http://127.0.0.1:8000/docs   (API'yi test etme sayfası)
"""

import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "todos.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # satırlara sözlük gibi erişmek için: row["title"]
    return conn


def init_db() -> None:
    """Uygulama ilk açıldığında tabloyu oluşturur (varsa dokunmaz)."""
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                done       INTEGER NOT NULL DEFAULT 0,          -- 0 = yapılmadı, 1 = yapıldı
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
            """
        )


def row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
        "created_at": row["created_at"],
    }


# ---------------------------------------------------------------------------
# 2) VERİ MODELLERİ (Pydantic)
# ---------------------------------------------------------------------------
# Frontend'den gelen JSON'un doğru biçimde olup olmadığını FastAPI bunlarla kontrol eder.
# Yanlış veri gelirse otomatik olarak 422 hatası döner.

class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None


class Todo(BaseModel):
    id: int
    title: str
    done: bool
    created_at: str


# ---------------------------------------------------------------------------
# 3) UYGULAMA
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # sunucu açılırken bir kere çalışır
    yield


app = FastAPI(title="To-do API", lifespan=lifespan)


# ---------------------------------------------------------------------------
# 4) API UÇ NOKTALARI (endpoints)
# ---------------------------------------------------------------------------
#   GET    /api/todos        -> tüm görevleri listele
#   POST   /api/todos        -> yeni görev ekle
#   PATCH  /api/todos/{id}   -> görevi güncelle (başlık veya yapıldı bilgisi)
#   DELETE /api/todos/{id}   -> görevi sil

@app.get("/api/todos", response_model=list[Todo])
def list_todos():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM todos ORDER BY done, id DESC").fetchall()
    return [row_to_dict(r) for r in rows]


@app.post("/api/todos", response_model=Todo, status_code=201)
def create_todo(data: TodoCreate):
    title = data.title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="Görev boş olamaz")
    with get_db() as conn:
        # "?" yer tutucusu SQL injection saldırılarına karşı korur. Asla f-string ile SQL yazma.
        cur = conn.execute("INSERT INTO todos (title) VALUES (?)", (title,))
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (cur.lastrowid,)).fetchone()
    return row_to_dict(row)


@app.patch("/api/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, data: TodoUpdate):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Görev bulunamadı")

        title = data.title.strip() if data.title is not None else row["title"]
        done = int(data.done) if data.done is not None else row["done"]
        conn.execute("UPDATE todos SET title = ?, done = ? WHERE id = ?", (title, done, todo_id))
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    return row_to_dict(row)


@app.delete("/api/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Görev bulunamadı")


# ---------------------------------------------------------------------------
# 5) FRONTEND DOSYALARI
# ---------------------------------------------------------------------------
# static/ klasöründeki HTML, CSS ve JS dosyalarını da aynı sunucu verir.

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")
