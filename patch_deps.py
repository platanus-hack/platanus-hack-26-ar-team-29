with open("backend/app/api/deps.py", "r") as f:
    content = f.read()

lines = content.split('\n')
new_lines = []
for line in lines:
    if line.strip() in [
        "from app.services.chat import ChatService",
        "from app.services.plans import PlanService",
        "from app.services.connections import ConnectionService",
        "from app.services.portfolio import PortfolioService",
        "from app.services.profiler import ProfilerService",
        "from app.ai.anthropic import AnthropicClient",
        "from app.config import get_settings",
        "from app.services.onchain import OnchainService",
        "from app.services.defi import DefiService"
    ]:
        # wait, they are also at the top now! I only want to remove indented ones.
        pass

# Instead of that, let's just use regex or check indentation.
import re
new_content = re.sub(r'^\s+from app\.services.*import.*\n', '', content, flags=re.MULTILINE)
new_content = re.sub(r'^\s+from app\.ai\.anthropic.*import.*\n', '', new_content, flags=re.MULTILINE)
new_content = re.sub(r'^\s+from app\.config import get_settings\n', '', new_content, flags=re.MULTILINE)

with open("backend/app/api/deps.py", "w") as f:
    f.write(new_content)
