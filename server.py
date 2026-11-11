"""Local development server; Python 3.10+, no package installation."""
import argparse
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlsplit
from game import Game, RuleError

WEB = Path(__file__).parent / 'web'
STATIC = {'/':('index.html','text/html'),'/index.html':('index.html','text/html'),
          '/styles.css':('styles.css','text/css'),'/game.js':('game.js','text/javascript'),
          '/art.js':('art.js','text/javascript')}


def make_server(game, host='127.0.0.1', port=0):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, code, body, kind='application/json', cookie=None):
            if isinstance(body,dict):
                body = json.dumps(body,ensure_ascii=True).encode()
            self.send_response(code)
            self.send_header('Content-Type',kind+'; charset=utf-8')
            self.send_header('Content-Length',str(len(body)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Referrer-Policy','same-origin')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'")
            if cookie:
                self.send_header('Set-Cookie',cookie)
            self.end_headers()
            self.wfile.write(body)

        def valid_host(self):
            hostname = urlsplit('http://'+self.headers.get('Host','')).hostname
            return hostname in ('localhost','127.0.0.1','::1',host)

        def token(self):
            cookie = SimpleCookie()
            try:
                cookie.load(self.headers.get('Cookie',''))
                return cookie['tw_session'].value if 'tw_session' in cookie else ''
            except Exception:
                return ''

        def do_GET(self):
            if not self.valid_host():
                return self.respond(403,{'error':'Unrecognized host.'})
            path = urlsplit(self.path).path
            if path == '/api/state':
                try:
                    return self.respond(200,game.state(self.token()))
                except RuleError as exc:
                    return self.respond(401,{'error':str(exc)})
            if path in STATIC:
                name,kind = STATIC[path]
                try:
                    return self.respond(200,(WEB/name).read_bytes(),kind)
                except OSError:
                    pass
            self.respond(404,{'error':'Not found.'})

        def do_POST(self):
            origin = self.headers.get('Origin')
            if not self.valid_host() or (origin and origin!='http://'+self.headers.get('Host','')):
                return self.respond(403,{'error':'Use the game from its own browser tab.'})
            try:
                length = int(self.headers.get('Content-Length','0'))
                if not 0 < length <= 4096:
                    return self.respond(413,{'error':'Request is too large or empty.'})
                if self.headers.get('Content-Type','').split(';')[0]!='application/json':
                    return self.respond(415,{'error':'Use JSON.'})
                body = json.loads(self.rfile.read(length))
                if not isinstance(body,dict):
                    raise RuleError('Request must be an object.')
                path = urlsplit(self.path).path
                if path == '/api/join':
                    token = game.join(body.get('name'),body.get('species'))
                    return self.respond(200,game.state(token),cookie=f'tw_session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=2592000')
                if path == '/api/action':
                    if not self.token():
                        return self.respond(401,{'error':'Join the world first.'})
                    return self.respond(200,game.action(self.token(),body.get('action'),body.get('args',{})))
                return self.respond(404,{'error':'Not found.'})
            except (ValueError,TypeError,UnicodeError) as exc:
                message = str(exc) if isinstance(exc,RuleError) else 'That request is not valid.'
                return self.respond(400,{'error':message})
    server = ThreadingHTTPServer((host,port),Handler)
    server.daemon_threads = True
    return server


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Snoopyland x Penguinland local game server')
    parser.add_argument('--port',type=int,default=8777)
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--db',type=Path,default=Path(__file__).parent/'data'/'world.sqlite3')
    args = parser.parse_args()
    server = make_server(Game(args.db),args.host,args.port)
    print(f'Two Worlds is ready: http://{args.host}:{server.server_port}',flush=True)
    print('Ctrl+C to stop. Progress is saved locally.',flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
