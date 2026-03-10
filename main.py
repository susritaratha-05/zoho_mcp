"""
main.py  —  Entry point for PD HR Chatbot FastAPI server.
Run: python main.py
"""

from api.app import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn
    from utils.config import settings

    uvicorn.run(
        "main:app",
        host      = settings.app_host,
        port      = settings.app_port,
        reload    = False,
        log_level = "info",
    )