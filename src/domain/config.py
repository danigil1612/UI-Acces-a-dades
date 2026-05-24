from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "test").lower()

if ENVIRONMENT not in {"test", "development", "production"}:
    raise ValueError("ENVIRONMENT ha de ser test, development o production")

DB_URL = os.getenv(
    f"DB_URL_{ENVIRONMENT.upper()}",
    "sqlite:///./f1_test.db" if ENVIRONMENT == "test" else "",
)

if not DB_URL:
    raise RuntimeError(f"Falta DB_URL_{ENVIRONMENT.upper()}")
