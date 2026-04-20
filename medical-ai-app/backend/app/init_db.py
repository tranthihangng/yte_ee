from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parents[1]
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from app.core.database import Base, engine  # noqa: E402
from app.models import *  # noqa: F401,F403,E402


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("Đã khởi tạo database thành công.")


if __name__ == "__main__":
    init_db()
