import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from multiprocessing import Process
import websockets
from datetime import datetime
import json
import os
from jinja2 import Environment, FileSystemLoader

logging.basicConfig(level=logging.INFO)

DATA_FILE = "storage/data.json"

if not os.path.exists("storage"):
    os.makedirs("storage")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/":
            self.send_html_file("index.html")
        elif parsed_url.path == "/message":
            self.send_html_file("message.html")
        elif parsed_url.path == "/read":
            self.show_messages()
        elif parsed_url.path.startswith("/static/"):
            self.send_static_file(parsed_url.path[1:])
        else:
            self.send_html_file("error.html", 404)

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        parsed_data = parse_qs(post_data.decode("utf-8"))
        username = parsed_data.get("username")[0]
        message = parsed_data.get("message")[0]

        message_data = {
            "username": username,
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
        }

        self.save_message_to_json(message_data)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        file_path = os.path.join(BASE_DIR, "pages", "message_sent.html")
        with open(file_path, "rb") as file:
            self.wfile.write(file.read())

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        file_path = os.path.join(BASE_DIR, "pages", filename)
        with open(file_path, "rb") as file:
            self.wfile.write(file.read())

    def send_static_file(self, filename, status=200):
        try:
            file_path = os.path.join(BASE_DIR, filename)
            with open(file_path, "rb") as file:
                self.send_response(status)
                if filename.endswith(".css"):
                    self.send_header("Content-type", "text/css")
                elif filename.endswith(".png"):
                    self.send_header("Content-type", "image/png")
                elif filename.endswith(".svg"):
                    self.send_header("Content-type", "image/svg+xml")
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_html_file("error.html", 404)

    def save_message_to_json(self, message_data):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        data[message_data["timestamp"]] = {
            "username": message_data["username"],
            "message": message_data["message"],
        }

        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def show_messages(self):
        env = Environment(loader=FileSystemLoader("pages"))
        template = env.get_template("messages.html")

        try:
            with open(DATA_FILE, "r") as file:
                messages = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            messages = {}

        logging.info(f"Loaded {len(messages)} messages from {DATA_FILE}")

        html_content = template.render(messages=messages)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

def run_http_server():
    server_address = ("", 3000)
    httpd = HTTPServer(server_address, HttpHandler)
    logging.info("HTTP server started on port 3000")
    httpd.serve_forever()


if __name__ == "__main__":
    http_process = Process(target=run_http_server)

    http_process.start()

    http_process.join()