import sqlite3
from datetime import datetime

conn = sqlite3.connect("fichajes.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


def inicializar():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fichajes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER,
        dt_id INTEGER,
        jugador_id INTEGER,
        club_nombre TEXT,
        club_rol_nombre TEXT,
        division TEXT,
        jugador_rol_nombre TEXT,
        estado TEXT DEFAULT 'PENDING',
        fecha_creacion TEXT
    )
    """)
    conn.commit()


def crear_fichaje(guild_id, dt_id, jugador_id, club):
    cursor.execute(
        """INSERT INTO fichajes
        (guild_id, dt_id, jugador_id, club_nombre, club_rol_nombre, division, jugador_rol_nombre, fecha_creacion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (guild_id, dt_id, jugador_id, club["nombre"], club["rol_club"], club["division"], club["rol_jugador"],
         datetime.now().strftime("%d/%m/%Y %H:%M"))
    )
    conn.commit()
    return cursor.lastrowid


def obtener_fichaje(fichaje_id):
    cursor.execute("SELECT * FROM fichajes WHERE id = ?", (fichaje_id,))
    return cursor.fetchone()


def actualizar_estado(fichaje_id, estado):
    cursor.execute("UPDATE fichajes SET estado = ? WHERE id = ?", (estado, fichaje_id))
    conn.commit()


def cancelar_otras_pendientes(jugador_id, excepto_id):
    """Cuando un jugador acepta un fichaje, cualquier otra solicitud pendiente suya queda obsoleta."""
    cursor.execute(
        "UPDATE fichajes SET estado = 'CANCELLED' WHERE jugador_id = ? AND estado = 'PENDING' AND id != ?",
        (jugador_id, excepto_id)
    )
    conn.commit()


def obtener_pendientes():
    """Usado al reiniciar el bot para volver a activar los botones de solicitudes aún pendientes."""
    cursor.execute("SELECT id FROM fichajes WHERE estado = 'PENDING'")
    return cursor.fetchall()
  
