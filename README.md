# pact-ai — conexión con la IA

FastAPI + Gemini (Google AI Studio, capa gratuita). **Es únicamente la conexión con la IA**: recibe texto o archivos,
llama al modelo y devuelve una respuesta estructurada y ya validada. El backend de PACT está en el repo `pact-monad`, del
lado servidor de Next.js, que llama a este servicio con `AI_API_URL`. Aquí no hay estado, base de datos ni blockchain.

| Endpoint | Entra | Sale |
|---|---|---|
| `POST /structure-agreement` | `text` y/o `file` (PDF, imagen o texto en base64) | `title`, `description`, `amount_mon`, `days`, `category`, `keywords`, `rules` |
| `POST /review-evidence` | `requirements`, `rules`, `provider_note`, `evidence_url` | `summary`, `results` (por regla: `met`, `reasoning`, `evidence_excerpt`), `model` |
| `GET /health` | — | `{"status": "ok"}` |

El veredicto final (`cumple` / `revisar`) y la decisión de pagar **no se toman aquí**: este servicio solo evalúa regla por
regla. Next.js agrega el resultado y aplica los límites del contrato.

## Cómo se protege una decisión que puede mover dinero

- **El contenido del cliente y del proveedor es dato, nunca instrucción.** Va aislado entre etiquetas y se neutralizan
  las etiquetas de cierre para que no pueda salirse de su bloque.
- **Una regla solo cuenta como cumplida si el modelo cita un fragmento literal** que aparece de verdad en la nota o en
  el enlace de la entrega. Sin cita, o con una cita inventada, se marca como no cumplida.
- **Una regla que el modelo omite se marca como no cumplida.** Omitir nunca aprueba.
- El modelo no abre el enlace: solo ve su texto.

## Correr en local

```sh
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements-dev.txt
cp .env.example .env            # y pegar la GEMINI_API_KEY
uvicorn main:app --reload --port 8000
pytest                          # pruebas con Gemini simulado: no gastan cuota ni piden clave
```

## Variables

| Variable | Para qué |
|---|---|
| `GEMINI_API_KEY` | Clave de Google AI Studio. Solo en `.env`; nunca se sube ni llega al navegador. |
| `GEMINI_MODEL` | Modelo (por defecto `gemini-2.5-flash`). |
| `PACT_AI_SHARED_SECRET` | Si se define, las peticiones deben traer el mismo valor en la cabecera `x-pact-ai-secret`. Obligatorio en cuanto el servicio tenga una URL pública: sin él, cualquiera podría gastar tu cuota. En Next.js va como `AI_API_SECRET`. |
