import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from game import Game
from server import make_server


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.server = make_server(Game(Path(cls.temp.name)/'world.db'))
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temp.cleanup()

    def request(self, method, path, payload=None, headers=None):
        conn = http.client.HTTPConnection('127.0.0.1',self.port,timeout=5)
        body = json.dumps(payload) if payload is not None else None
        head = {'Content-Type':'application/json',**(headers or {})}
        conn.request(method,path,body,head)
        response = conn.getresponse()
        result = response.status,dict(response.getheaders()),response.read()
        conn.close()
        return result

    def test_join_sets_private_cookie_and_state_resumes(self):
        code,headers,body = self.request('POST','/api/join',{'name':'Pebble','species':'penguin'})
        self.assertEqual(code,200)
        self.assertIn('HttpOnly',headers.get('Set-Cookie',''))
        self.assertIn('SameSite=Strict',headers.get('Set-Cookie',''))
        code,headers,body = self.request('GET','/api/state',headers={'Cookie':headers['Set-Cookie'].split(';')[0]})
        self.assertEqual(code,200)
        self.assertEqual(json.loads(body)['player']['name'],'Pebble')
        self.assertEqual(headers['Cache-Control'],'no-store')

    def test_unauthenticated_state_is_401(self):
        self.assertEqual(self.request('GET','/api/state')[0],401)

    def test_cross_origin_mutations_are_rejected(self):
        self.assertEqual(self.request('POST','/api/join',{'name':'Maple','species':'dog'},
                                      {'Origin':'https://other.example'})[0],403)

    def test_non_object_json_is_rejected_without_crashing(self):
        self.assertEqual(self.request('POST','/api/join',[])[0],400)

    def test_oversized_integer_coordinate_returns_json_error(self):
        _,headers,_ = self.request('POST','/api/join',{'name':'Birch','species':'dog'})
        cookie = headers['Set-Cookie'].split(';')[0]
        code,_,body = self.request('POST','/api/action',
            {'action':'move','args':{'x':10**1000,'y':300}}, {'Cookie':cookie})
        self.assertEqual(code,400)
        self.assertIn('error',json.loads(body))

    def test_static_paths_cannot_escape_web_root(self):
        self.assertEqual(self.request('GET','/../game.py')[0],404)
        self.assertEqual(self.request('GET','/%2e%2e/game.py')[0],404)
        self.assertEqual(self.request('GET','/data/world.db')[0],404)


if __name__ == '__main__':
    unittest.main()
