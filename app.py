from flask import Flask, request, jsonify, render_template
import sqlite3
import os

DATABASE = "database.db"

app = Flask(__name__)


# ------

def init_db():

    conn = sqlite3.connect(DATABASE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            is_done INTEGER NOT NULL DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()


def get_all_tasks():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, is_done FROM tasks ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    tasks = []
    for r in rows:
        tasks.append({
            "id": r["id"],
            "title": r["title"],
            "description": r["description"],
            "is_done": bool(r["is_done"]),
        })
    return tasks


def get_task(task_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, is_done FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "is_done": bool(row["is_done"]),
    }


def create_task(title, description="", is_done=False):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, description, is_done) VALUES (?, ?, ?)",
        (title, description, int(is_done)),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_task(new_id)


def update_task(task_id, title, description="", is_done=False):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE tasks
        SET title = ?, description = ?, is_done = ?
        WHERE id = ?
        """,
        (title, description, int(is_done), task_id),
    )
    conn.commit()
    affected = cur.rowcount
    conn.close()
    if affected == 0:
        return None
    return get_task(task_id)


def delete_task(task_id):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    affected = cur.rowcount
    conn.close()
    return affected > 0



if not os.path.exists(DATABASE):
    init_db()
else:
    init_db()



@app.route("/api/tasks", methods=["GET"])
def api_get_all_tasks():
    """Получить все записи."""
    tasks = get_all_tasks()
    return jsonify(tasks), 200


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def api_get_task(task_id):
    """Получить одну запись по id."""
    task = get_task(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task), 200


@app.route("/api/tasks", methods=["POST"])
def api_create_task():
    """Создать запись."""
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "Field 'title' is required"}), 400

    title = data["title"]
    description = data.get("description", "")
    is_done = bool(data.get("is_done", False))

    task = create_task(title, description, is_done)
    return jsonify(task), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def api_update_task(task_id):
    """Обновить запись."""
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "Field 'title' is required"}), 400

    title = data["title"]
    description = data.get("description", "")
    is_done = bool(data.get("is_done", False))

    task = update_task(task_id, title, description, is_done)
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task), 200


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def api_delete_task(task_id):
    """Удалить запись."""
    ok = delete_task(task_id)
    if not ok:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"status": "deleted"}), 200




@app.route("/")
def index():
    """Главная страница с интерфейсом работы с задачами."""
    return render_template("index.html")


if __name__ == "__main__":

    app.run(debug=True)
