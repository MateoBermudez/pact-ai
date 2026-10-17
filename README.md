# pact-ai — conexión con la IA

FastAPI + Gemini (Google AI Studio, capa gratuita). **Es únicamente la conexión con la IA**: recibe texto o archivos,
llama al modelo y devuelve una respuesta estructurada y ya validada. El backend de PACT está en el repo `pact-monad`, del
lado servidor de Next.js, que llama a este servicio con `AI_API_URL`. Aquí no hay estado, base de datos ni blockchain.

Desplegado en Vercel (https://pact-ai-eight.vercel.app); cada push a `main` lo redespliega.

| Endpoint | Entra | Sale |
|---|---|---|
| `POST /structure-agreement` | `text`, `file` (PDF, DOCX, imagen o texto en base64), y para ajustar un borrador `previous` + `feedback`; basta con uno | `title`, `description`, `amount_mon`, `days`, `category`, `keywords`, `rules` |
| `POST /review-evidence` | `requirements`, `rules`, `provider_note`, `evidence_url`, `evidence_text` (opcional, hasta 30.000 caracteres: el texto de la entrega, que la IA lee entero y puede citar) | `summary`, `results` (por regla: `met`, `reasoning`, `evidence_excerpt`), `model` |
| `POST /screen-applicant` | `listing`, `applicant` (perfil, habilidades, portafolio, reputación), `proposal`, `client_preferences` | `verdict` (`accept`, `review`, `reject`), `score` 0-100, `summary`, `strengths`, `concerns`, `model` |
| `GET /health` | — | `{"status": "ok"}` |

El veredicto final (`cumple` / `revisar`) y la decisión de pagar **no se toman aquí**: este servicio solo evalúa regla por
regla. Next.js agrega el resultado y aplica los límites del contrato.

Archivos admitidos en `file`: `application/pdf`, `image/png`, `image/jpeg`, `image/webp`, `text/plain`, `text/markdown`
y DOCX (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`, se convierte a texto). Máximo 7 MB.
El contenido real se comprueba contra el tipo declarado: un PDF que no empieza con `%PDF` se rechaza con 415.

## Cómo se protege una decisión que puede mover dinero

- **El contenido del cliente y del proveedor es dato, nunca instrucción.** Va aislado entre etiquetas y se neutralizan
  las etiquetas de cierre para que no pueda salirse de su bloque.
- **Una regla solo cuenta como cumplida si el modelo cita un fragmento literal** que aparece de verdad en la nota o en
  el enlace de la entrega. Sin cita, o con una cita inventada, se marca como no cumplida.
- **Una regla que el modelo omite se marca como no cumplida.** Omitir nunca aprueba.
- El modelo no abre el enlace: solo ve su texto.

## Modelos y tiempos

- `GEMINI_MODEL` es el principal y `GEMINI_FALLBACK_MODEL` el de respaldo. Si el principal falla por cupo (429), caída
  (5xx), tiempo agotado o respuesta con formato inválido, se prueba el de respaldo dentro del mismo presupuesto de tiempo.
  Un error no recuperable (por ejemplo 400) no se reintenta.
- Los modelos `gemini-2.5-*` ya no están disponibles para cuentas nuevas: el valor por defecto es `gemini-3.5-flash-lite`.
- Gemini exige un plazo mínimo de 10 s por intento, así que cada intento dura al menos eso.
- El razonamiento interno se desactiva en los modelos flash (baja latencia y costo): `thinking_budget=0` en 2.5 y
  `thinking_level=MINIMAL` en 3.x, que no aceptan lo mismo.
- La respuesta de `/review-evidence` informa en `model` el modelo que realmente respondió.
- `/screen-applicant` nunca acepta con puntaje menor de 70 ni rechaza con puntaje mayor de 45: en ese caso devuelve `review`.
- `/structure-agreement` devuelve la descripción como documento por secciones (contexto, alcance, requisitos, condiciones, entrega, por definir) y de 8 a 15 palabras clave para el emparejamiento.

## Arquitectura

Paquete `pact_ai/`, por capas. Las dependencias van hacia abajo: `api → services → (llm, prompts, ingestion) → schemas / core`.

```
pact_ai/
├── main.py                 crea la app FastAPI (el main.py de la raíz solo la reexporta: uvicorn main:app sigue valiendo)
├── api/                    HTTP: routes/ (health, structure, review), router.py, error_handlers.py
├── services/               casos de uso
│   ├── structure.py        arma el prompt, llama al modelo y normaliza
│   ├── review.py           revisa la entrega
│   ├── verification.py     la regla de la cita literal
│   ├── normalize.py        limpia lo que devuelve el modelo (categoría, reglas, palabras clave)
│   └── generation.py       errores del modelo → errores del servicio (502, 503)
├── llm/gemini.py           cliente: cadena de modelos, presupuesto de tiempo, razonamiento por familia
├── prompts/                system/*.md (se editan sin tocar código), sanitize.py, structure.py, review.py
├── ingestion/              archivo en base64 → partes para el modelo (sniff.py, docx_reader.py, files.py)
├── schemas/                modelos Pydantic: files, structure, review
└── core/                   config.py, errors.py, security.py
tests/                      api/ (extremo a extremo con Gemini simulado) y unit/ (por módulo)
```

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
| `GEMINI_MODEL` | Modelo principal (por defecto `gemini-3.5-flash-lite`). |
| `GEMINI_FALLBACK_MODEL` | Modelo de respaldo (por defecto `gemini-3.1-flash-lite`). |
| `PACT_AI_SHARED_SECRET` | Si se define, las peticiones deben traer el mismo valor en la cabecera `x-pact-ai-secret`. Obligatorio en cuanto el servicio tenga una URL pública: sin él, cualquiera podría gastar tu cuota. En Next.js va como `AI_API_SECRET`. |
| `MAX_FILE_BYTES`, `MAX_TEXT_FILE_CHARS` | Límites de archivo (7 MB y 20 000 caracteres por defecto). |
| `STRUCTURE_TIMEOUT_SECONDS`, `REVIEW_TIMEOUT_SECONDS`, `SCREENING_TIMEOUT_SECONDS` | Presupuesto de tiempo (40, 25 y 25 s por defecto; Next espera 45, 30 y 30). |

En la capa gratuita Google puede usar los datos enviados para mejorar sus productos: usa solo documentos de prueba.
