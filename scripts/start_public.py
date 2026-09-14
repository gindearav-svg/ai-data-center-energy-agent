import os

import uvicorn

from scripts.build_database import main as build_database


def main() -> None:
    """Rebuild the database and start the deterministic public demo."""
    os.environ["PUBLIC_DEMO"] = "1"
    build_database()

    uvicorn.run(
        "src.energy_agent.api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
    )


if __name__ == "__main__":
    main()