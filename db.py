"""
Capa de base de datos — soporta SQLite (local) y PostgreSQL (nube)
Detecta DATABASE_URL automáticamente.
"""
import os, sqlite3

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
USE_POSTGRES = bool(DATABASE_URL)
DB_PATH = os.path.join(os.path.dirname(__file__), "resultados.db")

if USE_POSTGRES:
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        raise ImportError("psycopg2-binary es necesario para PostgreSQL. Ejecuta: pip install psycopg2-binary")


class _Cursor:
    def __init__(self, cur):
        self._c = cur

    def fetchall(self):
        rows = self._c.fetchall()
        if not rows:
            return []
        return [dict(r) for r in rows]

    def fetchone(self):
        row = self._c.fetchone()
        return dict(row) if row else None


class Connection:
    def __init__(self):
        if USE_POSTGRES:
            url = DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            self._raw = psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            self._raw = sqlite3.connect(DB_PATH)
            self._raw.row_factory = sqlite3.Row

    def execute(self, sql, params=()):
        # PostgreSQL usa %s, SQLite usa ?
        if USE_POSTGRES:
            sql = sql.replace("?", "%s")
        cur = self._raw.cursor()
        cur.execute(sql, params)
        return _Cursor(cur)

    def commit(self):
        self._raw.commit()

    def close(self):
        self._raw.close()


def get_db():
    return Connection()


def init_db():
    conn = get_db()
    if USE_POSTGRES:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resultados (
                id SERIAL PRIMARY KEY,
                nombre TEXT,
                email TEXT,
                profesion TEXT,
                fecha TEXT,
                puntuacion INTEGER,
                porcentaje REAL,
                nivel TEXT,
                respuestas TEXT,
                tiempo_segundos INTEGER
            )
        """)
    else:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                email TEXT,
                profesion TEXT,
                fecha TEXT,
                puntuacion INTEGER,
                porcentaje REAL,
                nivel TEXT,
                respuestas TEXT,
                tiempo_segundos INTEGER
            )
        """)
    conn.commit()
    conn.close()
