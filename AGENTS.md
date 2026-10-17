# Instrucciones para agentes

## Commits

- **Nunca pongas a una IA como coautora de un commit.** Nada de `Co-Authored-By: Claude …` ni trailers equivalentes
  (Copilot, Codex, Gemini, Cursor, etc.), y nada de líneas tipo "Generated with …" en commits ni en PRs.
  El autor es la persona del equipo que hace el commit.

## Alcance de este servicio

- **`pact-ai` es únicamente la conexión con la IA**: recibe texto, llama a Gemini y devuelve una respuesta
  estructurada (`schemas.py`). Nada más.
- **El backend de PACT está en el repo `pact-monad`, del lado servidor de Next.js** (`app/app/api/*`, `app/lib/server/`).
  La lógica de negocio, la validación de reglas del acuerdo y cualquier contacto con la blockchain van allá, no aquí.
- Este servicio no guarda estado, no tiene base de datos, no conoce wallets ni contratos, y nunca firma ni mueve fondos.
- Solo lo llama el servidor de Next.js; no se expone al navegador.
