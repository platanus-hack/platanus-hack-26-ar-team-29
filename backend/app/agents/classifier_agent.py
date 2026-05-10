import json
from typing import Any

from anthropic import AsyncAnthropic

from app.config import get_settings

SYSTEM_PROMPT = """You are an expert financial transaction classifier for Argentine users. 
You will be provided with a JSON list of raw financial transactions.
Your job is to classify each one according to the following taxonomy:

- "income": Salary, dividends, incoming deposits.
- "necessary_expense": Rent, groceries, utilities, basic life needs.
- "discretionary_expense": Dining out, entertainment, luxury, subscriptions.
- "safe_investment": ETFs, Treasury bills, low-risk roboadvisor, bonds.
- "risky_investment": Crypto, individual stocks, high-risk roboadvisor.
- "transfer": Moving money between own accounts (e.g. checking to investment).
- "fee": Bank fees, trade commissions, taxes.
- "other": Anything else.

For each transaction, you must output:
1. "uuid": The uuid from the raw transaction so we can link it back.
2. "category": The exact category string from the list above.
3. "merchant": A cleaned up, user-friendly name of the counterpart or asset (e.g. "Apple" instead of "AAPL", "Amazon" instead of "AMZN", "Wallbit Transfer").
4. "recurrence_hint": Either "monthly", "weekly", "yearly", "none", or "unknown".

Output ONLY valid JSON inside a tool call. Use the `submit_classifications` tool.
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
