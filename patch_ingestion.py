import re
with open("backend/app/services/ingestion.py", "r") as f:
    content = f.read()

new_content = re.sub(r'^\s+import json\n', '', content, flags=re.MULTILINE)
new_content = re.sub(r'^\s+from app\.config import get_settings\n', '', new_content, flags=re.MULTILINE)
new_content = re.sub(r'^\s+from app\.persistence\.session import session_factory\n', '', new_content, flags=re.MULTILINE)
new_content = re.sub(r'^\s+from app\.agents\.classifier_agent import classify_transactions\n', '', new_content, flags=re.MULTILINE)
new_content = re.sub(r'^\s+from app\.persistence\.models\.users import UserProfile\n', '', new_content, flags=re.MULTILINE)
new_content = re.sub(r'^\s+from app\.services\.context import recalculate_user_profile\n', '', new_content, flags=re.MULTILINE)

with open("backend/app/services/ingestion.py", "w") as f:
    f.write(new_content)
