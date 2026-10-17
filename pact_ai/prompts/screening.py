from pact_ai.prompts.loader import load_system_prompt
from pact_ai.prompts.sanitize import neutralize
from pact_ai.schemas import ScreenApplicantIn

SCREENING_SYSTEM = load_system_prompt("screening")


def _list(items: list[str]) -> str:
    return ", ".join(neutralize(item) for item in items) or "(ninguna)"


def screening_prompt(data: ScreenApplicantIn) -> str:
    listing, applicant, proposal = data.listing, data.applicant, data.proposal
    rules = "\n".join(f"- {neutralize(rule)}" for rule in listing.rules) or "(sin condiciones)"
    portfolio = (
        "\n".join(
            f"- {neutralize(item.title)}: {neutralize(item.description) or '(sin descripción)'}"
            for item in applicant.portfolio
        )
        or "(sin portafolio)"
    )
    rating = f"{applicant.provider_score:.1f} de 5" if applicant.provider_score is not None else "sin calificaciones"
    blocks = [
        (
            "<oportunidad>\n"
            f"Título: {neutralize(listing.title)}\n"
            f"Categoría: {neutralize(listing.category or '') or '(sin categoría)'}\n"
            f"Presupuesto: {listing.budget_mon if listing.budget_mon is not None else '(sin definir)'} MON\n"
            f"Plazo: {listing.deadline_days if listing.deadline_days is not None else '(sin definir)'} días\n"
            f"Palabras clave: {_list(listing.keywords)}\n"
            f"Descripción:\n{neutralize(listing.description) or '(sin descripción)'}\n"
            f"Condiciones de aceptación:\n{rules}\n"
            "</oportunidad>"
        ),
        (
            "<candidato>\n"
            f"Nombre: {neutralize(applicant.display_name) or '(sin nombre)'}\n"
            f"Presentación: {neutralize(applicant.bio) or '(sin presentación)'}\n"
            f"Habilidades: {_list(applicant.skills)}\n"
            f"Palabras clave del perfil: {_list(applicant.keywords)}\n"
            f"Disponibilidad: {neutralize(applicant.availability or '') or '(sin indicar)'}\n"
            f"Calificación como prestador: {rating}\n"
            f"Trabajos completados en PACT: {applicant.completed_jobs}\n"
            f"Portafolio:\n{portfolio}\n"
            "</candidato>"
        ),
        (
            "<propuesta>\n"
            f"Mensaje: {neutralize(proposal.message)}\n"
            f"Precio: {proposal.price_mon if proposal.price_mon is not None else '(el de la oportunidad)'} MON\n"
            f"Plazo: {proposal.days if proposal.days is not None else '(el de la oportunidad)'} días\n"
            "</propuesta>"
        ),
    ]
    if data.client_preferences.strip():
        blocks.append(f"<criterios_del_cliente>\n{neutralize(data.client_preferences.strip())}\n</criterios_del_cliente>")
    return "\n\n".join(blocks)
