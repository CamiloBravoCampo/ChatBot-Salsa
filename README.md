# Agente de IA — Guía paso a paso

Este README está diseñado para los aprendices de ADSO que quiere aprender acerca de los agentes inteligentes de IA - Chatbot desde la perspectiva del (frontend + backend). Contiene instrucciones claras para configurar, ejecutar y extender el agente.
# Agente de IA — Guía paso a paso

Este README guía a un aprendiz para entender, ejecutar y extender el proyecto `agente` (frontend + backend). Está escrito en pasos claros y ordenados.

**Estructura de carpetas (resumen)**

```
agente/
    .env                # (opcional) variables de entorno
    app.py              # servidor Flask, rutas y lógica de endpoints
    config.py           # carga de configuración y variables de entorno
    requirements.txt    # dependencias Python
    README.md           # este archivo
    model/
        agente.py         # lógica del agente: funciones `build_messages` y `generate_response`
    static/
        app.js            # frontend JS: UI y llamadas a /api/chat
        styles.css
        img/
    templates/
        index.html        # interfaz principal
```

1) Introducción rápida
- **Qué es**: un micro-proyecto con backend en Flask y frontend (HTML+JS) que permite conversar con un agente IA (implementación de ejemplo con `google.generativeai`).

2) Requisitos
- Python 3.10+.
- Git (opcional).

3) Preparar el entorno (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si ya tienes un virtualenv en `env/` usa `.\env\Scripts\Activate.ps1`.

4) Instalar dependencias

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

Dependencias importantes (fijas en este proyecto): `Flask==2.3.3`, `python-dotenv==1.2.1`, `google-generativeai==0.8.5`, `gunicorn==20.1.0`.

5) Variables de entorno
- Crea un archivo `.env` junto a `app.py` con, por ejemplo:

```
FLASK_ENV=development
SECRET_KEY=una_clave_segura
API_KEY_EXTERNA=tu_api_key
```

- `config.py` lee las variables necesarias; ajusta nombres si corresponde.
- Nota: puedes generar `API_KEY_EXTERNA` en AI Studio (https://aistudio.google.com/) desde la sección de credenciales/API keys; copia el valor y guárdalo en `.env`.

6) Ejecutar la app (desarrollo)

```powershell
python app.py
```

Abre `http://127.0.0.1:5000/` en tu navegador.

7) Endpoints principales
- `GET /` — sirve `index.html`.
- `POST /api/chat` — recibe JSON con `{ message, history }` y devuelve `{ success, response, history }`.

    - Request ejemplo:

    ```json
    { "message": "Hola agente", "history": [] }
    ```

    - Response ejemplo (éxito):

    ```json
    { "success": true, "response": "Texto de respuesta", "history": [] }
    ```

8) Cómo interactúa el frontend
- `static/app.js` mantiene `conversationHistory` en memoria, muestra mensajes y hace `fetch('/api/chat', { method: 'POST', body: JSON })`.
- Muestra un indicador de "Pensando…" mientras espera la respuesta.

9) Detalle: `model/agente.py` (qué hace y por qué)

`SYSTEM_PROMPT`:
    - Es un mensaje guía que define la identidad, límites y tono del asistente. En este proyecto el prompt instruye al asistente a responder solo sobre temas del SENA y a negarse educadamente en caso contrario.
    - Tip: sé explícito (identidad, restricciones, tono) y proporciona ejemplos de salida si necesitas formato rígido.

`build_messages(user_message, history)`:
    - Convierte el historial local (objetos con `sender` y `text`) y el mensaje actual en la estructura que espera el SDK (`role` y `parts`).
    - Mantener roles correctos (`user` vs `model` vs `system`) ayuda al modelo a entender el contexto.

`generate_response(user_message, history, api_key, model_name)`:
    - Flujo: obtiene la clave (`api_key` o `GEMINI_API_KEY` desde `config.py`), configura el cliente `genai`, construye mensajes con `build_messages`, instancia `GenerativeModel` con `system_instruction=SYSTEM_PROMPT` y llama a `model.generate_content(...)`.
    - Devuelve el texto de la respuesta o lanza error si la clave no está configurada.
    - Buenas prácticas: manejar excepciones, recortar historial largo y aplicar settings de seguridad/moderación.

10) Detalle: `app.py` (recepción, validación y respuesta)

`POST /api/chat` (resumen del flujo):
    1. `data = request.get_json()` para obtener el JSON.
    2. `user_message = data.get('message', '').strip()` y `history = data.get('history', [])`.
    3. Si `user_message` está vacío, devolver `400` con `{ 'error': 'Message cannot be empty' }`.
    4. Llamar a `generate_response(user_message, history)` y obtener `assistant_message`.
    5. Devolver `{ 'success': True, 'response': assistant_message, 'history': history }`.
    6. Si ocurre excepción, devolver `500` con un mensaje genérico y registrar `details` en logs (no enviar secretos al cliente).

Notas prácticas:
    - El frontend ya actualiza el historial localmente; si prefieres que el servidor lo haga, agrega la respuesta al `history` antes de retornarla.
    - En producción usa `gunicorn` y no `debug=True`.

11) Probar el endpoint desde PowerShell

```powershell
$body = @{ message = 'Hola agente'; history = @() } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/chat' -Method Post -Body $body -ContentType 'application/json'
```

12) Buenas prácticas y siguientes pasos - sugeridos
- No subir `.env` ni claves a repositorios públicos.
- Añadir logging estructurado en `app.py` y manejar excepciones en `model/agente.py`.
- Extensiones sugeridas: persistir historial (SQLite), añadir autenticación, limitar longitud de prompts, cachear respuestas frecuentes.

13) Despliegue
- Desarrollo: `python app.py`.
- Producción (Linux): usar `gunicorn --bind 0.0.0.0:8000 app:app` y un reverse-proxy (NGINX).

14) Recursos
- Flask: https://flask.palletsprojects.com/
- Google AI Studio / Gemini docs: https://aistudio.google.com/
