import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler

MODELO = "meta-llama/llama-3.1-8b-instruct"
MAX_MENSAJES = 40      # mensajes de conversación que se envían al modelo
MAX_CARACTERES = 8000  # tamaño máximo por mensaje (lo que pase se recorta)
MAX_SISTEMA = 4000     # tamaño máximo del mensaje de sistema
ROLES = ("system", "user", "assistant")
URL_OPENROUTER = "https://openrouter.ai/api/v1/chat/completions"


def limpiar_mensajes(recibidos):
    """Descarta lo que no tenga forma de mensaje y recorta los textos largos."""
    validos = [
        m for m in recibidos
        if isinstance(m, dict) and m.get("role") in ROLES and isinstance(m.get("content"), str)
    ]
    sistema = [
        {"role": "system", "content": m["content"][:MAX_SISTEMA]}
        for m in validos if m["role"] == "system"
    ][:1]
    conversacion = [
        {"role": m["role"], "content": m["content"][:MAX_CARACTERES]}
        for m in validos if m["role"] != "system"
    ][-MAX_MENSAJES:]
    return sistema, conversacion


class handler(BaseHTTPRequestHandler):

    def responder(self, estado, cuerpo):
        datos = json.dumps(cuerpo).encode("utf-8")
        self.send_response(estado)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        self.responder(405, {"error": "Método no permitido"})

    def do_POST(self):
        api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("VITE_OPENROUTER_KEY")
        if not api_key:
            return self.responder(500, {"error": "Falta la API Key en el servidor."})

        try:
            largo = int(self.headers.get("Content-Length", 0))
            cuerpo = json.loads(self.rfile.read(largo) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self.responder(400, {"error": "El cuerpo no es JSON válido."})

        recibidos = cuerpo.get("messages") if isinstance(cuerpo, dict) else None
        if not isinstance(recibidos, list) or not recibidos:
            return self.responder(400, {"error": "Formato de mensajes inválido."})

        sistema, conversacion = limpiar_mensajes(recibidos)
        if not conversacion:
            return self.responder(400, {"error": "No hay mensajes para enviar."})

        peticion = urllib.request.Request(
            URL_OPENROUTER,
            data=json.dumps({"model": MODELO, "messages": sistema + conversacion}).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://mediassist-rural.vercel.app",
                "X-Title": "MediAssist Rural",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(peticion, timeout=25) as r:
                estado, texto = r.status, r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            estado, texto = e.code, e.read().decode("utf-8", errors="replace")
        except Exception as e:
            return self.responder(500, {"error": f"Fallo de red hacia OpenRouter: {e}"})

        try:
            datos = json.loads(texto)
        except json.JSONDecodeError:
            return self.responder(502, {"error": f"Respuesta no válida de OpenRouter (HTTP {estado})."})

        if estado >= 400:
            mensaje = (datos.get("error") or {}).get("message") if isinstance(datos, dict) else None
            return self.responder(estado, {
                "error": mensaje or f"OpenRouter devolvió HTTP {estado}",
                "code": estado,
            })

        return self.responder(200, datos)
