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

def run_http_server():
    server_address = ("", 3000)
    httpd = HTTPServer(server_address, HttpHandler)
    logging.info("HTTP server started on port 3000")
    httpd.serve_forever()


if __name__ == "__main__":
    http_process = Process(target=run_http_server)

    http_process.start()

    http_process.join()
