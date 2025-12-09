"""Lógica del agente conversacional.

Este módulo encapsula la construcción de mensajes y la interacción con el
cliente generativo (`google.generativeai`). Contiene:
- `SYSTEM_PROMPT`: la instrucción de sistema que guía el comportamiento del
  asistente institucional.
- `build_messages(...)`: convierte el historial local y el mensaje del usuario
  en la estructura mínima que usa el SDK.
- `generate_response(...)`: orquesta la llamada al modelo generativo y devuelve
  la respuesta en texto.

Buenas prácticas aplicadas:
- docstrings y tipado para facilitar lectura y autocompletado.
- logging de errores para depuración (sin exponer claves ni detalles al cliente).
"""

from typing import List, Dict, Any, Optional
import logging

import google.generativeai as genai

from config import GEMINI_API_KEY


logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """Eres un asistente institucional del SENA (Servicio Nacional de Aprendizaje) en Colombia.

RESTRICCIONES IMPORTANTES:
- Solo puedes responder sobre temas relacionados con el SENA
- Temas permitidos:
  * Programas de formación del SENA
  * Metodologías de formación, proyectos de investigación, innovación y emprendimiento del SENA
  * Información general sobre servicios del SENA (formación, certificación por competencias, emprendimiento, Agencia Pública de Empleo, etc.)
  * Orientación académica o institucional relacionada directamente con el SENA

- Si el usuario pregunta algo que NO esté relacionado con el SENA, DEBES RESPONDER ÚNICAMENTE CON:
  "Lo siento, solo puedo responder preguntas relacionadas con el SENA y sus servicios institucionales."

TONO:
- Mantén siempre un tono respetuoso, claro y pedagógico
- Sé conciso pero informativo
- Utiliza lenguaje institucional profesional

Recuerda: Si la pregunta no está claramente relacionada con el SENA, recházala educadamente."""


def build_messages(user_message: str, history: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Construye la lista de mensajes que se pasará al cliente generativo.

    Args:
        user_message: texto actual del usuario.
        history: lista opcional de mensajes previos. Cada elemento se espera que
            sea un diccionario con claves como `sender` y `text` (por ejemplo,
            `{ 'sender': 'Usuario', 'text': 'Hola' }`).

    Returns:
        Lista de mensajes en la forma [{'role': 'user'|'model', 'parts': [texto]}].

    Nota: esta función crea una representación mínima usada por el SDK. Si el
    proveedor requiere otra estructura (p. ej. objetos más complejos), adaptar
    aquí la transformación.
    """

    messages: List[Dict[str, Any]] = []
    for msg in history or []:
        # Mapear remitente local a rol esperado por el SDK.
        role = 'user' if msg.get('sender') == 'Usuario' else 'model'
        messages.append({'role': role, 'parts': [msg.get('text', '')]})

    # Añadir el mensaje actual al final del contexto.
    messages.append({'role': 'user', 'parts': [user_message]})
    return messages


def generate_response(
    user_message: str,
    history: Optional[List[Dict[str, Any]]] = None,
    api_key: Optional[str] = None,
    model_name: str = "gemini-flash-latest",
) -> str:
    """Genera la respuesta del asistente usando el cliente `google.generativeai`.

    Este wrapper:
      - valida la presencia de la API key (vía `api_key` o `GEMINI_API_KEY`);
      - configura el cliente `genai`;
      - construye mensajes con `build_messages`;
      - instancia `GenerativeModel` con `SYSTEM_PROMPT` como `system_instruction`;
      - invoca `generate_content` y devuelve el texto resultante.

    Args:
        user_message: texto actual del usuario.
        history: historial de la conversación (opcional).
        api_key: clave opcional que sobrescribe la de `config.GEMINI_API_KEY`.
        model_name: nombre del modelo a usar (por defecto `gemini-flash-latest`).

    Returns:
        Texto con la respuesta generada por el modelo.

    Raises:
        ValueError: si no se encuentra ninguna API key.
        RuntimeError: si ocurre un error al solicitar la generación (el error
            original se registra en logs para diagnóstico).
    """

    key = api_key or GEMINI_API_KEY
    if not key:
        logger.error('API key no encontrada: revisar GEMINI_API_KEY en config')
        raise ValueError("GEMINI_API_KEY environment variable not set")

    # Configurar cliente: no registramos la clave en logs ni la mostramos.
    genai.configure(api_key=key)

    messages = build_messages(user_message, history or [])

    # Crear instancia del modelo generativo con la instrucción de sistema.
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_PROMPT,
    )

    try:
        # Actualmente se envía solo el texto del último mensaje; si se desea
        # enviar todo el contexto, adaptar esta llamada según la API del SDK.
        prompt_text = messages[-1]['parts'][0]

        response = model.generate_content(
            prompt_text,
            safety_settings=[
                {
                    'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
                    'threshold': 'BLOCK_NONE',
                }
            ],
        )

        # El SDK puede devolver un objeto complejo; intentar extraer `text`.
        return getattr(response, 'text', str(response))

    except Exception:
        # Registrar excepción completa para facilitar la depuración en servidor.
        logger.exception('Error al generar respuesta desde el modelo generativo')
        # Lanzar un error genérico hacia capas superiores para que lo manejen.
        raise RuntimeError('Error al generar la respuesta del asistente')