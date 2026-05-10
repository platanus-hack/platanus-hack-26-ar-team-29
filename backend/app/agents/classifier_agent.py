import json
from typing import Any

from anthropic import AsyncAnthropic

from app.config import get_settings

SYSTEM_PROMPT = """Sos un experto clasificador de transacciones financieras para usuarios de Argentina.
Se te proveerá una lista en JSON de transacciones financieras crudas.
Tu trabajo es clasificar cada una de acuerdo a la siguiente taxonomía:

- "Ingreso": Salario, dividendos, depósitos entrantes.
- "Gasto Necesario": Alquiler, supermercado, servicios, necesidades básicas.
- "Gasto Discrecional": Salidas a comer, entretenimiento, lujos, suscripciones.
- "Inversión Segura": ETFs, bonos del tesoro, roboadvisor de bajo riesgo, bonos.
- "Inversión de Riesgo": Crypto, acciones individuales, roboadvisor de alto riesgo.
- "Transferencia": Mover dinero entre cuentas propias (ej. de cuenta corriente a inversión).
- "Comisión/Impuesto": Cargos bancarios, comisiones de trading, impuestos.
- "Otro": Cualquier otra cosa.

Para cada transacción, debes emitir:
1. "uuid": El uuid de la transacción cruda para poder enlazarla.
2. "category": El string exacto de la categoría de la lista de arriba.
3. "merchant": Un nombre limpio y amigable para el usuario de la contraparte o activo (ej. "Apple" en vez de "AAPL", "Amazon" en vez de "AMZN", "Transferencia Wallbit").
4. "recurrence_hint": Debe ser "mensual", "semanal", "anual", "ninguna", o "desconocido".

Emite ÚNICAMENTE un JSON válido dentro del llamado a la herramienta. Usá la herramienta `submit_classifications`.
"""


async def classify_transactions(transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not transactions:
        return []

    settings = get_settings()
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    transactions_json = json.dumps(transactions, default=str)

    tools = [
        {
            "name": "submit_classifications",
            "description": "Submit the classified transactions.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "uuid": {"type": "string"},
                                "category": {"type": "string"},
                                "merchant": {"type": "string"},
                                "recurrence_hint": {"type": "string"},
                            },
                            "required": ["uuid", "category", "merchant", "recurrence_hint"],
                        },
                    }
                },
                "required": ["results"],
            },
        }
    ]

    response = await client.messages.create(
        model=settings.anthropic_model,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Classify these transactions:\n{transactions_json}"}
        ],
        tools=tools,
        tool_choice={"type": "tool", "name": "submit_classifications"},
    )

    for content in response.content:
        if content.type == "tool_use" and content.name == "submit_classifications":
            return content.input.get("results", [])

    return []
