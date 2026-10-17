# pact-ai — servicio de IA (Python)

FastAPI + Gemini (Google AI Studio, capa gratuita). **Es únicamente la conexión con la IA**: recibe texto, llama al modelo y devuelve una respuesta estructurada. El backend de PACT está en el repo `pact-monad`, del lado servidor de Next.js, que llama a este servicio desde sus rutas `/api/*` usando la variable `AI_API_URL`.

| Endpoint | Entra | Sale |
|---|---|---|
| `POST /structure-agreement` | texto libre del cliente | `description`, `amount_mon`, `days` |
| `POST /review-evidence` | requisitos, nota del proveedor, enlace | `verdict` (`cumple` / `revisar`), `reason` |
| `GET /health` | — | `{"status": "ok"}` |

Los modelos están en `schemas.py`. Los dos endpoints de IA devuelven 501 hasta el entregable D.

## Correr en local

```sh
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # y pegar la GEMINI_API_KEY
uvicorn main:app --reload --port 8000
```

La clave de Gemini vive solo en `.env`. Nunca se sube al repositorio ni se expone al navegador.
