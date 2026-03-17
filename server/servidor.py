from fastapi import FastAPI

app = FastAPI()

estado = {"teclado": "desbloqueado"}

@app.get("/")
def home():
    return estado

@app.get("/bloquear")
def bloquear():
    estado["teclado"] = "bloqueado"
    print("Estado: BLOQUEADO")
    return {"status": "ok"}

@app.get("/desbloquear")
def desbloquear():
    estado["teclado"] = "desbloqueado"
    print("Estado: DESBLOQUEADO")
    return {"status": "ok"}