from pathlib import Path

STATIC_DIR = Path(__file__).parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"


def app(environ, start_response):
    html_file = INDEX_HTML.read_bytes()
    start_response(
        "200 OK",
        [("Content-Type", "text/html"), ("Content-Length", str(len(html_file)))],
    )
    return [html_file]
