with open("backend/app/agents/chat_agent.py", "r") as f:
    content = f.read()

import re
content = re.sub(r'^AGENT_FALLBACK_MODEL\s*=\s*.*?\n', '', content, flags=re.MULTILINE)

with open("backend/app/agents/chat_agent.py", "w") as f:
    f.write(content)
