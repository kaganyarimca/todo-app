// To-do uygulaması: frontend
// Bu dosya backend'deki API'yi fetch() ile çağırır ve sonucu ekrana çizer.

const API = "/api/todos";

let todos = [];        // sunucudan gelen görevler
let filter = "all";    // all | open | done

const listEl = document.getElementById("list");
const emptyEl = document.getElementById("empty");
const errorEl = document.getElementById("error");
const countEl = document.getElementById("count");
const form = document.getElementById("new-form");
const input = document.getElementById("new-title");

// ---------------------------------------------------------------------------
// API çağrıları
// ---------------------------------------------------------------------------

// Tüm istekler bu fonksiyondan geçer: hata olursa ekranda gösterir.
async function request(url, options = {}) {
  errorEl.hidden = true;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let message = `Sunucu hatası (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") message = body.detail;
    } catch (_) { /* gövde JSON değilse varsayılan mesaj kalır */ }
    throw new Error(message);
  }
  return res.status === 204 ? null : res.json();
}

async function loadTodos() {
  todos = await request(API);
  render();
}

async function addTodo(title) {
  const todo = await request(API, { method: "POST", body: JSON.stringify({ title }) });
  todos.unshift(todo);
  render();
}

async function updateTodo(id, changes) {
  const updated = await request(`${API}/${id}`, { method: "PATCH", body: JSON.stringify(changes) });
  todos = todos.map((t) => (t.id === id ? updated : t));
  render();
}

async function deleteTodo(id) {
  await request(`${API}/${id}`, { method: "DELETE" });
  todos = todos.filter((t) => t.id !== id);
  render();
}

function showError(err) {
  errorEl.textContent = err.message || "Bir şeyler ters gitti.";
  errorEl.hidden = false;
}

// ---------------------------------------------------------------------------
// Ekrana çizme
// ---------------------------------------------------------------------------

function render() {
  // Sunucudaki sıralamanın aynısı: önce yapılmamışlar, sonra en yeni en üstte
  todos.sort((a, b) => a.done - b.done || b.id - a.id);

  const visible = todos.filter((t) =>
    filter === "open" ? !t.done : filter === "done" ? t.done : true
  );

  listEl.replaceChildren(...visible.map(renderItem));
  emptyEl.hidden = visible.length > 0;

  const left = todos.filter((t) => !t.done).length;
  countEl.textContent = `${left} görev kaldı`;
}

function renderItem(todo) {
  const li = document.createElement("li");
  li.className = "item" + (todo.done ? " done" : "");

  const check = document.createElement("input");
  check.type = "checkbox";
  check.checked = todo.done;
  check.setAttribute("aria-label", "Tamamlandı");
  check.addEventListener("change", () =>
    updateTodo(todo.id, { done: check.checked }).catch(showError)
  );

  // textContent kullanıyoruz, innerHTML değil: kullanıcının yazdığı metin HTML olarak çalışmasın (XSS koruması)
  const title = document.createElement("span");
  title.className = "title";
  title.textContent = todo.title;
  title.addEventListener("dblclick", () => startEdit(li, title, todo));

  const del = document.createElement("button");
  del.className = "del";
  del.type = "button";
  del.textContent = "×";
  del.setAttribute("aria-label", "Sil");
  del.addEventListener("click", () => deleteTodo(todo.id).catch(showError));

  li.append(check, title, del);
  return li;
}

// Çift tıklayınca başlığı düzenlenebilir bir kutuya çevirir
function startEdit(li, titleEl, todo) {
  const edit = document.createElement("input");
  edit.className = "edit";
  edit.value = todo.title;
  edit.maxLength = 200;
  titleEl.replaceWith(edit);
  edit.focus();
  edit.select();

  let finished = false;
  const finish = (save) => {
    if (finished) return;
    finished = true;
    const value = edit.value.trim();
    if (save && value && value !== todo.title) {
      updateTodo(todo.id, { title: value }).catch((e) => { showError(e); render(); });
    } else {
      render();
    }
  };
  edit.addEventListener("keydown", (e) => {
    if (e.key === "Enter") finish(true);
    if (e.key === "Escape") finish(false);
  });
  edit.addEventListener("blur", () => finish(true));
}

// ---------------------------------------------------------------------------
// Olaylar
// ---------------------------------------------------------------------------

form.addEventListener("submit", async (e) => {
  e.preventDefault(); // formun sayfayı yenilemesini engelle
  const title = input.value.trim();
  if (!title) return;
  try {
    await addTodo(title);
    input.value = "";
  } catch (err) {
    showError(err);
  }
});

document.querySelectorAll(".filters button").forEach((btn) => {
  btn.addEventListener("click", () => {
    filter = btn.dataset.filter;
    document.querySelectorAll(".filters button").forEach((b) => b.classList.toggle("active", b === btn));
    render();
  });
});

loadTodos().catch(showError);
