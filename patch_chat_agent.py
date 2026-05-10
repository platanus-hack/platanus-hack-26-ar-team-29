import re
with open("backend/app/agents/chat_agent.py", "r") as f:
    content = f.read()

imports = """
import structlog
from anthropic import AsyncAnthropic
from app.config import get_settings
from app.persistence.repositories.chat import ChatRepository
from app.persistence.repositories.plans import PlanRepository
from app.services.chat import _message_to_api
from app.services.plans import _plan_to_dict
from app.agents.wallbit_tools import _request
"""

# Insert imports after the last absolute import block
content = content.replace("from app.agents.wallbit_tools import wallbit_mcp_server", "from app.agents.wallbit_tools import wallbit_mcp_server\n" + imports)

# Remove the inline imports
lines = content.split('\n')
new_lines = []
for line in lines:
    if line.strip() in [
        "from app.agents.wallbit_tools import _request",
        "from app.persistence.repositories.chat import ChatRepository",
        "from app.services.chat import _message_to_api",
        "from app.persistence.repositories.plans import PlanRepository",
        "from app.services.plans import _plan_to_dict",
        "from anthropic import AsyncAnthropic",
        "from app.config import get_settings",
        "import structlog"
    ]:
        continue
    new_lines.append(line)

with open("backend/app/agents/chat_agent.py", "w") as f:
    f.write('\n'.join(new_lines))
