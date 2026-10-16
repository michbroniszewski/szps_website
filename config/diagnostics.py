"""Raport konfiguracji bazy do logu — bez haseł.

Wołany przy błędzie połączenia z bazą (config/maintenance.py). Bez SSH to
jedyny sposób, żeby sprawdzić, co aplikacja faktycznie odczytała z .env.
"""

from datetime import datetime

from django.conf import settings
from dotenv import dotenv_values


def db_config_report() -> str:
    db = settings.DATABASES["default"]
    env_file = settings.ENV_FILE
    lines = [f"plik .env: {env_file}"]

    file_values = {}
    if env_file.exists():
        raw = env_file.read_bytes()
        stat = env_file.stat()
        bom = "TAK" if raw.startswith(b"\xef\xbb\xbf") else "nie"
        eol = "CRLF" if b"\r\n" in raw else "LF"
        lines.append(
            f"  rozmiar {stat.st_size} B, zmieniony "
            f"{datetime.fromtimestamp(stat.st_mtime):%Y-%m-%d %H:%M:%S}, "
            f"BOM: {bom}, końce linii: {eol}"
        )
        text = raw.decode("utf-8", errors="replace")
        for key in ("DB_ENGINE", "DB_USER", "DB_PASSWORD", "DB_NAME", "DB_HOST"):
            count = sum(1 for line in text.splitlines() if line.lstrip().startswith(key + "="))
            if count != 1:
                lines.append(f"  UWAGA: linia {key}= występuje {count}×")
        file_values = dotenv_values(env_file)
    else:
        lines.append("  PLIKU NIE MA")

    password = db.get("PASSWORD") or ""
    file_password = file_values.get("DB_PASSWORD") or ""
    lines += [
        f"silnik: {db['ENGINE']}",
        f"użytkownik: {db.get('USER')!r} (w pliku: {file_values.get('DB_USER')!r})",
        f"baza: {db.get('NAME')!r}, host: {db.get('HOST')!r}, port: {db.get('PORT')!r}",
        f"hasło: długość {len(password)}, zgodne z plikiem: {'tak' if password == file_password else 'NIE'}, "
        f"spacje na brzegach: {'TAK' if password != password.strip() else 'nie'}",
        f"zmienne ustawione w środowisku przed .env: {', '.join(settings.ENV_PRESET_KEYS) or 'brak'}",
    ]
    return "\n".join(lines)
