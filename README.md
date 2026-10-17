# pact-ai — servicio de IA (Python)

FastAPI + Gemini (Google AI Studio). Es únicamente la conexión con la IA: recibe texto y archivos, llama al modelo y devuelve JSON estructurado. Sin base de datos ni estado persistente. El backend de PACT (Next.js) lo llama desde el servidor con `AI_API_URL`; el navegador nunca habla con él.

## Endpoints

| Endpoint | Entrada | Salida |
|---|---|---|
| `POST /structure-agreement` (JSON) | `text`, o `previous` + `feedback` para refinar | borrador del acuerdo |
| `POST /structure-agreement/files` (multipart) | `text`, `files[]` (PDF, DOCX, PNG, JPG, WEBP, TXT, MD), `previous` (JSON), `feedback` | borrador del acuerdo |
| `POST /review-evidence` (JSON) | `requirements`, `provider_note`, `evidence_url` | recomendación |
| `POST /review-evidence/files` (multipart) | los mismos campos + `files[]` como evidencia | recomendación |
| `GET /health` | — | estado y modelo configurado |

### Respuesta de `structure-agreement`

`status` (`ok` o `needs_clarification`), `description` (≤ 500 bytes, límite del contrato), `amount_mon`, `days`, `title`, `deliverables`, `acceptance_criteria`, `category`, `skills`, `suggested_milestones`, `warnings`, `questions` y `meta`.

Si falta el monto o el plazo, `status` es `needs_clarification`, el campo faltante viene en `null` y `questions` trae lo que hay que preguntarle al usuario.

### Respuesta de `review-evidence`

`verdict` (`cumple` o `revisar`), `reason`, `checklist[]`, `confidence` y `meta`. Solo es `cumple` si la IA lo indica y todos los ítems del checklist están cumplidos; si no hay checklist, es `revisar`. El enlace no se abre.

### `meta`

`model`, `source` (`gemini`, `cache` o `fallback`), `input_tokens`, `output_tokens`, `latency_ms`. El backend puede usarlo para contabilizar créditos.

## Arquitectura

Paquete `pact_ai/`, por capas. Cada módulo tiene una sola responsabilidad y las dependencias van hacia abajo: `api → services → (llm, prompts, ingestion, fallback) → schemas / core`.

```
pact_ai/
├── main.py                    crea la app FastAPI
├── api/                       HTTP: rutas, manejo de errores, lectura de formularios
│   ├── router.py              junta los routers
│   ├── routes/                health.py, agreements.py, reviews.py
│   ├── uploads.py             lee archivos subidos y el borrador previo
│   └── error_handlers.py      errores de dominio → respuestas HTTP
├── services/                  casos de uso (orquestan, sin HTTP ni SDK)
│   ├── structure_agreement.py
│   ├── review_evidence.py
│   ├── agreement_output.py    normaliza montos, días y descripción
│   └── caching.py
├── llm/                       acceso al modelo
│   ├── base.py                protocolo LLM
│   └── gemini.py              cliente Gemini: reintentos, modelo de respaldo, tokens
├── prompts/                   todo lo que se le dice al modelo
│   ├── system/                structure.md, review.md (se editan sin tocar código)
│   ├── loader.py              carga los .md
│   ├── sanitize.py            neutraliza etiquetas inyectadas por el usuario
│   ├── blocks.py              bloques comunes (documentos, adjuntos)
│   ├── structure.py           arma el contenido de structure-agreement
│   └── review.py              arma el contenido de review-evidence
├── ingestion/                 archivos subidos → partes para el modelo
│   ├── sniff.py               detecta el tipo por el contenido
│   ├── docx_reader.py         DOCX → texto
│   ├── ingest.py              validación de límites y clasificación
│   └── models.py
├── fallback/                  respaldo sin IA (regex)
│   ├── parsing.py
│   └── rules.py
├── schemas/                   modelos Pydantic: common.py, agreement.py, review.py
└── core/                      config.py, errors.py, cache.py, security.py, dependencies.py
tests/                         api/ (extremo a extremo con LLM falso) y unit/ (por módulo)
scripts/smoke_gemini.py        prueba contra Gemini real
```

Para agregar un endpoint nuevo: esquemas en `schemas/`, prompt en `prompts/system/`, constructor en `prompts/`, caso de uso en `services/`, ruta en `api/routes/`.

## Comportamiento

- Modelo principal `GEMINI_MODEL` y respaldo `GEMINI_FALLBACK_MODEL`; si el primero falla por cupo, caída o respuesta inválida, se intenta con el segundo dentro de un presupuesto de 13 s (Next corta a los 15 s).
- Si Gemini no responde y la solicitud es solo texto, `structure-agreement` devuelve un borrador por reglas (`source: fallback`). `review-evidence` devuelve `revisar`.
- Caché en memoria de 10 minutos por entrada, para repetir la demo sin gastar cupo.
- Archivos: máximo 3, 8 MB cada uno y 15 MB en total. Los PDF e imágenes los lee Gemini; los DOCX se convierten a texto.
- Si `INTERNAL_API_TOKEN` está definido, las rutas exigen la cabecera `X-Internal-Token`.

## Correr en local

```sh
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env          # y pegar la GEMINI_API_KEY
uvicorn pact_ai.main:app --reload --port 8000
```

Pruebas: `pytest`. Prueba contra Gemini real: `python scripts/smoke_gemini.py`.

La clave de Gemini vive solo en `.env`. Nunca se sube al repositorio ni se expone al navegador. En la capa gratuita Google puede usar los datos enviados para mejorar sus productos: usa solo documentos de prueba.
