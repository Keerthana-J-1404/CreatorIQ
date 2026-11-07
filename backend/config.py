import ipaddress
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

LOCALHOST_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://localhost:3000",
)


def _parse_cors_origins(value: str | None) -> list[str]:
    additional_origins: list[str] = []
    for candidate in (value or "").split(","):
        origin = candidate.strip()
        if not origin:
            continue
        if origin in LOCALHOST_CORS_ORIGINS or origin in additional_origins:
            continue
        if "*" in origin:
            raise ValueError("CORS_ORIGINS must contain explicit origins, not wildcards.")
        if any(character.isspace() for character in origin):
            raise ValueError(f"Invalid CORS origin: {origin!r}")

        try:
            parsed = urlsplit(origin)
            hostname = parsed.hostname
            port = parsed.port
        except ValueError as exc:
            raise ValueError(f"Invalid CORS origin: {origin!r}") from exc

        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or hostname is None
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path
            or parsed.query
            or parsed.fragment
            or "?" in origin
            or "#" in origin
            or parsed.netloc.endswith(":")
        ):
            raise ValueError(f"Invalid CORS origin: {origin!r}")

        if port is not None and not 0 <= port <= 65535:
            raise ValueError(f"Invalid CORS origin port: {origin!r}")

        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            if re.fullmatch(r"[0-9.]+", hostname) or not _is_valid_domain(hostname):
                raise ValueError(f"Invalid CORS origin host: {origin!r}")

        additional_origins.append(origin)
    return [*LOCALHOST_CORS_ORIGINS, *additional_origins]


def _is_valid_domain(hostname: str) -> bool:
    if len(hostname) > 253:
        return False
    if hostname.endswith(".."):
        return False
    normalized_hostname = hostname[:-1] if hostname.endswith(".") else hostname
    labels = normalized_hostname.split(".")
    if not labels or any(not label for label in labels):
        return False
    return all(
        len(label) <= 63
        and re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", label)
        for label in labels
    )


CORS_ORIGINS = _parse_cors_origins(os.getenv("CORS_ORIGINS"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL", "https://hindsight.vectorize.io")
