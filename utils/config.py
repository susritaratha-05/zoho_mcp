import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    # ── LLM Provider ──────────────────────────────────────────────────────────
    # Set LLM_PROVIDER in .env to: groq | ollama | openai
    llm_provider:  str = os.getenv("LLM_PROVIDER", "groq").lower()

    # Groq
    groq_api_key:  str = os.getenv("GROQ_API_KEY", "")
    groq_model:    str = os.getenv("GROQ_MODEL",   "llama-3.3-70b-versatile")

    # Ollama
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model:    str = os.getenv("OLLAMA_MODEL",    "llama3")

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model:   str = os.getenv("OPENAI_MODEL",   "gpt-4o")

    # ── Zoho ──────────────────────────────────────────────────────────────────
    zoho_client_id:     str = os.getenv("ZOHO_CLIENT_ID",     "")
    zoho_client_secret: str = os.getenv("ZOHO_CLIENT_SECRET", "")
    zoho_refresh_token: str = os.getenv("ZOHO_REFRESH_TOKEN", "")
    zoho_access_token:  str = os.getenv("ZOHO_ACCESS_TOKEN",  "")
    zoho_redirect_uri:  str = os.getenv("ZOHO_REDIRECT_URI",  "https://www.zoho.com/people")
    zoho_token_url:     str = os.getenv("ZOHO_TOKEN_URL",     "https://accounts.zoho.in/oauth/v2/token")
    zoho_base_url:      str = os.getenv("ZOHO_BASE_URL",      "https://people.zoho.in")

    # ── MCP Server ────────────────────────────────────────────────────────────
    mcp_server_url: str = os.getenv("MCP_SERVER_URL", "http://localhost:8001/sse")

    # ── FastAPI ───────────────────────────────────────────────────────────────
    app_host:    str = os.getenv("APP_HOST",  "0.0.0.0")
    app_port:    int = int(os.getenv("APP_PORT", "8000"))
    fastapi_url: str = os.getenv("FASTAPI_URL", "http://localhost:8000")

    # ── App ───────────────────────────────────────────────────────────────────
    allowed_domain: str = os.getenv("ALLOWED_DOMAIN", "prodevans.com")


settings = Settings()