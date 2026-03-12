import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path.home() / '.podscribe' / 'history.json'


def load_history() -> list:
    if not HISTORY_FILE.exists():
        return []

    try:
        data = json.loads(HISTORY_FILE.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return []

    return data if isinstance(data, list) else []


def add_record(url, title, status, output_files, error=None):
    history_dir = HISTORY_FILE.parent
    history_dir.mkdir(parents=True, exist_ok=True)

    records = load_history()
    records.append({
        'url': url,
        'title': title,
        'timestamp': datetime.now().astimezone().isoformat(),
        'status': status,
        'output_files': [str(path) for path in output_files],
        'error': error,
    })

    HISTORY_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
