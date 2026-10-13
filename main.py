import sqlite3
import re
import sqlite3
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from pysentimiento import create_analyzer

app = FastAPI(title="API de Análisis de Sentimientos")
analyzer = create_analyzer(task="sentiment", lang="es")
DB = "sentimientos.db"

# ---------- Reglas de apoyo para negaciones ----------
POS_PAL = {"feliz", "contento", "contenta", "alegre", "bien", "bueno", "buena"}
NEG_PAL = {
    "triste", "mal", "malo", "mala", "molesto", "molesta", "enojado", "enojada",
    "enfadado", "enfadada", "furioso", "furiosa", "preocupado", "preocupada",
    "estresado", "estresada", "deprimido", "deprimida", "nervioso", "nerviosa",
    "asustado", "asustada", "decepcionado", "decepcionada",
}
NEGACIONES = {"no", "nunca", "jamás", "jamas", "tampoco"}
CORTES = {"pero", "aunque", "sino", "y", "porque", ",", ".", ";", "!", "?"}

def esta_negada(tokens, i):
    for j in range(i - 1, max(i - 6, -1), -1):
        if tokens[j] in CORTES:
            return False
        if tokens[j] in NEGACIONES:
            return True
    return False

def ajustar(p, texto):
    tokens = re.findall(r"\w+|[,.;!?]", texto.lower())
    palabras = set(tokens)
    if "ni" in palabras and palabras & POS_PAL and palabras & NEG_PAL:
        return {"NEG": 0.10, "NEU": 0.70, "POS": 0.20}
    indices = [i for i, w in enumerate(tokens) if w in NEG_PAL]
    if indices and all(esta_negada(tokens, i) for i in indices):
        return {"NEG": 0.10, "NEU": 0.60, "POS": 0.30}
    return p

# ---------- Base de datos ----------
def conectar():
    return sqlite3.connect(DB)

with conectar() as con:
    con.execute("""CREATE TABLE IF NOT EXISTS comentarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT, comentario TEXT,
        negativo REAL, neutro REAL, positivo REAL,
        fecha TEXT DEFAULT CURRENT_TIMESTAMP)""")

# ---------- API ----------
class Entrada(BaseModel):
    usuario: str = "Anónimo"
    comentario: str = Field(min_length=1, max_length=1000)

@app.post("/analizar")
def analizar(datos: Entrada):
    p = ajustar(analyzer.predict(datos.comentario).probas, datos.comentario)
    res = {
        "usuario": datos.usuario,
        "comentario": datos.comentario,
        "negativo": round(p["NEG"] * 100, 1),
        "neutro": round(p["NEU"] * 100, 1),
        "positivo": round(p["POS"] * 100, 1),
    }
    with conectar() as con:
        con.execute(
            "INSERT INTO comentarios (usuario, comentario, negativo, neutro, positivo) VALUES (?,?,?,?,?)",
            (res["usuario"], res["comentario"], res["negativo"], res["neutro"], res["positivo"]),
        )
    return res

@app.get("/historial")
def historial():
    with conectar() as con:
        filas = con.execute(
            "SELECT usuario, comentario, negativo, neutro, positivo FROM comentarios ORDER BY id DESC LIMIT 10"
        ).fetchall()
    return [dict(zip(["usuario", "comentario", "negativo", "neutro", "positivo"], f)) for f in filas]

# Esta línea va AL FINAL: sirve la página web
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pysentimiento import create_analyzer

app = FastAPI(title="API de Análisis de Sentimientos")
analyzer = create_analyzer(task="sentiment", lang="es")
DB = "sentimientos.db"

def conectar():
    return sqlite3.connect(DB)

with conectar() as con:
    con.execute("""CREATE TABLE IF NOT EXISTS comentarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT, comentario TEXT,
        negativo REAL, neutro REAL, positivo REAL,
        fecha TEXT DEFAULT CURRENT_TIMESTAMP)""")

class Entrada(BaseModel):
    usuario: str = "Anónimo"
    comentario: str

@app.post("/analizar")
def analizar(datos: Entrada):
    p = ajustar(analyzer.predict(datos.comentario).probas, datos.comentario)
    res = {
        "usuario": datos.usuario,
        "comentario": datos.comentario,
        "negativo": round(p["NEG"] * 100, 1),
        "neutro": round(p["NEU"] * 100, 1),
        "positivo": round(p["POS"] * 100, 1),
    }
    with conectar() as con:
        con.execute(
            "INSERT INTO comentarios (usuario, comentario, negativo, neutro, positivo) VALUES (?,?,?,?,?)",
            (res["usuario"], res["comentario"], res["negativo"], res["neutro"], res["positivo"]),
        )
    return res

@app.get("/historial")
def historial():
    with conectar() as con:
        filas = con.execute(
            "SELECT usuario, comentario, negativo, neutro, positivo FROM comentarios ORDER BY id DESC LIMIT 10"
        ).fetchall()
    return [dict(zip(["usuario", "comentario", "negativo", "neutro", "positivo"], f)) for f in filas]

# Esta línea va AL FINAL: sirve la página web
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")