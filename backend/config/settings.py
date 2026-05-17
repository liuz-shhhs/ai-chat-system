import os
from pathlib import Path


def _load_env_file():
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


try:
    from dotenv import load_dotenv
except ImportError:
    _load_env_file()
else:
    load_dotenv()


DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "chat_db"),
    "charset": "utf8mb4",
}
