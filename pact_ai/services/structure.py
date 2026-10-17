from google.genai import types

from pact_ai.core.config import Settings
from pact_ai.ingestion import file_contents
from pact_ai.prompts import STRUCTURE_SYSTEM, refinement_prompt, structure_prompt
from pact_ai.schemas import StructureAgreementIn, StructureAgreementOut, StructureDraft
from pact_ai.services.generation import generate
from pact_ai.services.normalize import to_structure


async def structure_agreement(body: StructureAgreementIn, settings: Settings) -> StructureAgreementOut:
    contents: list[types.Part | str] = []
    if prompt := structure_prompt(body.text):
        contents.append(prompt)
    if body.file is not None:
        contents.extend(file_contents(body.file, settings))
    contents.extend(refinement_prompt(body.previous, body.feedback))

    generation = await generate(StructureDraft, STRUCTURE_SYSTEM, contents, settings.structure_timeout_seconds)
    return to_structure(generation.parsed)
