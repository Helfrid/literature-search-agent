#!/usr/bin/env python3
"""Simple HTTP server for article scoring app."""

import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

# Base directory for data files
DATA_DIR = Path(__file__).parent.parent / "data"
PROMPTS_PATH = (
    Path(__file__).parent.parent
    / "src"
    / "literature_search_agent"
    / "prompts.py"
)


def _parse_classifications() -> list[str]:
    """Parse classification titles from prompts.py."""
    text = PROMPTS_PATH.read_text()
    return [t.strip() for t in re.findall(r"^### (.+)$", text, re.MULTILINE)]


class ScoringServerHandler(BaseHTTPRequestHandler):
    """HTTP request handler for scoring app."""

    def _set_headers(
        self, status: int = 200, content_type: str = "application/json"
    ) -> None:
        """Set response headers."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, data: Any, status: int = 200) -> None:
        """Send JSON response."""
        self._set_headers(status)
        self.wfile.write(json.dumps(data).encode())

    def _send_error(self, message: str, status: int = 400) -> None:
        """Send error response."""
        self._send_json({"error": message}, status)

    def do_OPTIONS(self) -> None:
        """Handle OPTIONS requests for CORS."""
        self._set_headers()

    def do_GET(self) -> None:
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/":
            # Serve index.html
            self._serve_file("index.html", "text/html")
        elif path == "/styles.css":
            self._serve_file("styles.css", "text/css")
        elif path == "/app.js":
            self._serve_file("app.js", "application/javascript")
        elif path == "/api/dates":
            self._handle_get_dates()
        elif path == "/api/classifications":
            self._handle_get_classifications()
        elif path.startswith("/api/papers/"):
            date = path.split("/")[-1]
            self._handle_get_papers(date)
        else:
            self._send_error("Not found", 404)

    def do_POST(self) -> None:
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/api/score":
            self._handle_set_score()
        elif path == "/api/classify":
            self._handle_set_classification()
        else:
            self._send_error("Not found", 404)

    def _serve_file(self, filename: str, content_type: str) -> None:
        """Serve static file."""
        try:
            file_path = Path(__file__).parent / filename
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self._send_error("File not found", 404)

    def _handle_get_classifications(self) -> None:
        """Get list of classification categories."""
        try:
            classifications = _parse_classifications()
            self._send_json(classifications)
        except (OSError, ValueError) as e:
            self._send_error(str(e), 500)

    def _handle_get_dates(self) -> None:
        """Get list of available dates."""
        try:
            dates = []
            for file_path in DATA_DIR.glob("papers_raw_*.json"):
                # Extract date from filename (papers_raw_2026-02-06.json)
                date = file_path.stem.replace("papers_raw_", "")
                dates.append(date)
            dates.sort(reverse=True)  # Most recent first
            self._send_json(dates)
        except OSError as e:
            self._send_error(str(e), 500)

    def _handle_get_papers(self, date: str) -> None:
        """Get papers for a specific date."""
        try:
            raw_path = DATA_DIR / f"papers_raw_{date}.json"
            manual_path = DATA_DIR / f"papers_for_manual_{date}.json"

            if not raw_path.exists() or not manual_path.exists():
                self._send_error("Papers not found for this date", 404)
                return

            with open(raw_path) as f:
                raw_papers = json.load(f)

            with open(manual_path) as f:
                manual_papers = json.load(f)

            # Ensure analysed field exists in both
            for paper in raw_papers:
                if "analysed" not in paper:
                    paper["analysed"] = False

            for paper in manual_papers:
                if "analysed" not in paper:
                    paper["analysed"] = False
                if "classification" not in paper:
                    paper["classification"] = "unassigned"

            self._send_json({"raw": raw_papers, "manual": manual_papers})

        except (OSError, json.JSONDecodeError, KeyError) as e:
            self._send_error(str(e), 500)

    def _handle_set_score(self) -> None:
        """Set score for a paper."""
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            date = data.get("date")
            pmid = data.get("pmid")
            score = data.get("score")

            if not all([date, pmid is not None, score is not None]):
                self._send_error("Missing required fields", 400)
                return

            raw_path = DATA_DIR / f"papers_raw_{date}.json"
            manual_path = DATA_DIR / f"papers_for_manual_{date}.json"

            # Update raw papers
            with open(raw_path) as f:
                raw_papers = json.load(f)

            for paper in raw_papers:
                if paper["pmid"] == pmid:
                    paper["analysed"] = True
                    break

            with open(raw_path, "w") as f:
                json.dump(raw_papers, f, indent=2)

            # Update manual papers
            with open(manual_path) as f:
                manual_papers = json.load(f)

            for paper in manual_papers:
                if paper["pmid"] == pmid:
                    paper["score"] = score
                    paper["analysed"] = True
                    break

            with open(manual_path, "w") as f:
                json.dump(manual_papers, f, indent=2)

            self._send_json({"success": True})

        except (OSError, json.JSONDecodeError, KeyError, ValueError) as e:
            self._send_error(str(e), 500)

    def _handle_set_classification(self) -> None:
        """Set classification for a paper."""
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            date = data.get("date")
            pmid = data.get("pmid")
            classification = data.get("classification")

            if not all([date, pmid is not None, classification]):
                self._send_error("Missing required fields", 400)
                return

            manual_path = DATA_DIR / f"papers_for_manual_{date}.json"

            with open(manual_path) as f:
                manual_papers = json.load(f)

            for paper in manual_papers:
                if paper["pmid"] == pmid:
                    paper["classification"] = classification
                    break

            with open(manual_path, "w") as f:
                json.dump(manual_papers, f, indent=2)

            self._send_json({"success": True})

        except (OSError, json.JSONDecodeError, KeyError, ValueError) as e:
            self._send_error(str(e), 500)

    def log_message(self, fmt: str, *args: Any) -> None:
        """Custom log message format."""
        print(f"[{self.log_date_time_string()}] {fmt % args}")


def run_server(port: int = 8000) -> None:
    """Run the HTTP server."""
    server_address = ("", port)
    httpd = HTTPServer(server_address, ScoringServerHandler)
    print(f"Starting server on port {port}...")
    print(f"Open http://localhost:{port} in your browser")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    run_server()
