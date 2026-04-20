from datetime import datetime
from uuid import uuid4


def generate_case_code() -> str:
    stamp = datetime.utcnow().strftime("%y%m%d")
    suffix = str(uuid4()).split("-")[0].upper()
    return f"CA{stamp}{suffix[:4]}"
