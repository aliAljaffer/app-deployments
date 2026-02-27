#!/usr/bin/env python3

"""
Simple CORS proxy for kubectl proxy
Wraps kubectl proxy and adds CORS headers to allow browser access
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
import sys

KUBECTL_PROXY = 'http://localhost:8001'
PROXY_PORT = 8002


class CORSProxyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        self.proxy_request()

    def do_POST(self):
        self.proxy_request()

    def do_PUT(self):
        self.proxy_request()

    def do_DELETE(self):
        self.proxy_request()

    def do_PATCH(self):
        self.proxy_request()

    def proxy_request(self):
        """Proxy the request to kubectl proxy"""
        url = f"{KUBECTL_PROXY}{self.path}"

        try:
            # Read request body if present
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(
                content_length) if content_length > 0 else None

            # Create request
            headers = {}
            if body:
                headers['Content-Type'] = self.headers.get(
                    'Content-Type', 'application/json')

            req = urllib.request.Request(
                url, data=body, headers=headers, method=self.command)

            # Make request
            with urllib.request.urlopen(req) as response:
                # Send response
                self.send_response(response.status)
                self.send_cors_headers()

                # Forward headers
                for key, value in response.headers.items():
                    if key.lower() not in ['server', 'date', 'connection']:
                        self.send_header(key, value)

                self.end_headers()

                # Forward body
                self.wfile.write(response.read())

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(500)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(str(e).encode())

    def send_cors_headers(self):
        """Add CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods',
                         'GET, POST, PUT, DELETE, PATCH, OPTIONS')
        self.send_header('Access-Control-Allow-Headers',
                         'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')

    def log_message(self, format, *args):
        """Custom log format"""
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")


if __name__ == '__main__':
    print('=========================================')
    print('  CORS Proxy Server for kubectl proxy')
    print('=========================================')
    print()
    print(f'Listening on: http://localhost:{PROXY_PORT}')
    print(f'Proxying to:  {KUBECTL_PROXY}')
    print()
    print('Make sure kubectl proxy is running:')
    print('  kubectl proxy --port=8001')
    print()
    print('Update dashboard API URL to:')
    print(f'  http://localhost:{PROXY_PORT}')
    print()
    print('Press Ctrl+C to stop')
    print('=========================================')
    print()

    try:
        server = HTTPServer(('localhost', PROXY_PORT), CORSProxyHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down...')
        server.shutdown()
