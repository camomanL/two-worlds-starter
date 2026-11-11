"""Transactional, server-authoritative game state."""
from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
import secrets
import sqlite3
import time
from content import EMOTES, ITEMS, PROJECT_GOAL, QUESTS, RECIPES, WORLDS


class RuleError(ValueError):
    """An invalid player action, safe to display to the client."""


def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise RuleError('That quantity or slot is not valid.')
    return value


class Game:
    def __init__(self, path, clock=None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.clock = clock or time.time
        with self.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS players (id TEXT PRIMARY KEY,
                  token_hash TEXT UNIQUE NOT NULL, data TEXT NOT NULL, seen REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS projects (world TEXT PRIMARY KEY, deliveries INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, text TEXT NOT NULL, at REAL NOT NULL);
            ''')
            for world in WORLDS:
                db.execute('INSERT OR IGNORE INTO projects(world) VALUES (?)', (world,))

    @contextmanager
    def db(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        try:
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def token_hash(token):
        if not isinstance(token, str) or not 20 <= len(token) <= 128:
            raise RuleError('Join the world first.')
        return hashlib.sha256(token.encode()).hexdigest()

    def load(self, db, token):
        row = db.execute('SELECT data FROM players WHERE token_hash=?', (self.token_hash(token),)).fetchone()
        if row is None:
            raise RuleError('Your session was not found. Join again.')
        return json.loads(row['data'])

    def save(self, db, player):
        db.execute('UPDATE players SET data=?, seen=? WHERE id=?', (json.dumps(player),self.clock(),player['id']))

    def event(self, db, text):
        db.execute('INSERT INTO events(text,at) VALUES (?,?)', (text,self.clock()))
        db.execute('DELETE FROM events WHERE id NOT IN (SELECT id FROM events ORDER BY id DESC LIMIT 30)')

    def join(self, name, species):
        if not isinstance(name, str):
            raise RuleError('Choose a short nickname.')
        name = ' '.join(name.split())
        if not 2 <= len(name) <= 16 or any(not (c.isalnum() or c in ' -_') for c in name):
            raise RuleError('Nickname: 2–16 letters, numbers, spaces, hyphens or underscores.')
        if species not in ('dog','penguin'):
            raise RuleError('Choose a dog or a penguin.')
        token = secrets.token_urlsafe(32)
        now = self.clock()
        p = {'id':secrets.token_hex(8),'name':name,'species':species,'world':'snoopy',
             'x':510.0,'y':430.0,'coins':30,'xp':0,'inventory':{'wood':2,'berries':2},
             'stats':{},'claimed':[],'home':['']*6,'cooldowns':{},'last_move':now,
             'fish':None,'emote':'','emote_until':0,'joined':now}
        with self.db() as db:
            db.execute('INSERT INTO players VALUES (?,?,?,?)', (p['id'],self.token_hash(token),json.dumps(p),now))
        return token

    def snapshot(self, db, p):
        now = self.clock()
        others = []
        for row in db.execute('SELECT data FROM players WHERE seen>? AND id<>? LIMIT 100', (now-20,p['id'])):
            friend = json.loads(row['data'])
            others.append({k:friend[k] for k in ('id','name','species','world','x','y','emote','emote_until')})
        public = {k:v for k,v in p.items() if k not in ('fish','last_move','joined')}
        return {'player':public,'players':others,'now':now,
                'projects':{r['world']:r['deliveries'] for r in db.execute('SELECT * FROM projects')},
                'project_goal':PROJECT_GOAL,
                'events':[dict(r) for r in db.execute('SELECT text,at FROM events ORDER BY id DESC LIMIT 5')],
                'content':{'worlds':WORLDS,'items':ITEMS,'recipes':RECIPES,'quests':QUESTS}}

    def state(self, token):
        with self.db() as db:
            p = self.load(db, token)
            self.save(db,p)
            return self.snapshot(db,p)

    @staticmethod
    def near(p, point, radius=105):
        if math.hypot(p['x']-point[0],p['y']-point[1]) > radius:
            raise RuleError('Walk a little closer first.')

    @staticmethod
    def spend(p, cost):
        if any(p['inventory'].get(item,0)<qty for item,qty in cost.items()):
            raise RuleError('You need a few more materials for that.')
        for item,qty in cost.items():
            p['inventory'][item] -= qty

    @staticmethod
    def add(p, item, qty):
        p['inventory'][item] = p['inventory'].get(item,0)+qty

    @staticmethod
    def stat(p, key, qty=1):
        p['stats'][key] = p['stats'].get(key,0)+qty

    def action(self, token, action, args):
        if not isinstance(args,dict):
            raise RuleError('Action details must be an object.')
        with self.db() as db:
            p = self.load(db,token)
            w = WORLDS[p['world']]
            now = self.clock()
            extra, message = {}, ''
            if action == 'move':
                x,y = args.get('x'),args.get('y')
                if any(type(v) not in (int,float) for v in (x,y)):
                    raise RuleError('Choose a valid location.')
                if not (90<=x<=1110 and 200<=y<=640):
                    raise RuleError('Stay on the island paths.')
                allowance = min(4.0,max(0.0,now-p['last_move']))*240+12
                if math.hypot(x-p['x'],y-p['y']) > allowance:
                    raise RuleError('Slow down a little!')
                p.update(x=float(x),y=float(y),last_move=now)
            elif action == 'gather':
                n = next((n for n in w['nodes'] if n['id']==args.get('node')),None)
                if n is None:
                    raise RuleError('That resource is not here.')
                self.near(p,(n['x'],n['y']),95)
                if p['cooldowns'].get(n['id'],0)>now:
                    raise RuleError('This spot is growing back. Explore another spot!')
                self.add(p,n['item'],n['qty'])
                self.stat(p,'gather_'+n['item'],n['qty'])
                p['xp'] += 3
                p['cooldowns'][n['id']] = now+12
                message = f"+{n['qty']} {ITEMS[n['item']]['name']}"
            elif action == 'travel':
                self.near(p,w['portal'])
                p['world'] = 'penguin' if p['world']=='snoopy' else 'snoopy'
                p.update(x=970.0,y=405.0,last_move=now,fish=None)
                self.stat(p,'visits_'+p['world'])
                message = 'Welcome to '+WORLDS[p['world']]['name']+'!'
            elif action == 'craft':
                self.near(p,w['workshop'],125)
                recipe = args.get('recipe')
                if recipe not in RECIPES:
                    raise RuleError('Choose a workshop recipe.')
                self.spend(p,RECIPES[recipe]['cost'])
                self.add(p,recipe,1)
                self.stat(p,'craft_'+recipe)
                p['xp'] += RECIPES[recipe]['xp']
                message = ITEMS[recipe]['name']+' crafted!'
            elif action == 'deliver':
                self.near(p,w['post'])
                self.spend(p,{'parcel':1})
                db.execute('UPDATE projects SET deliveries=deliveries+1 WHERE world=?',(p['world'],))
                self.stat(p,'deliveries')
                p['coins'] += 12
                p['xp'] += 20
                self.event(db,p['name']+' sent a neighbor parcel from '+w['name']+'.')
                message = 'Parcel delivered! +12 shells · +20 XP'
            elif action == 'claim':
                q = next((q for q in QUESTS if q['id']==args.get('quest')),None)
                if q is None or q['id'] in p['claimed']:
                    raise RuleError('That stamp has already been collected or does not exist.')
                if p['stats'].get(q['stat'],0)<q['goal']:
                    raise RuleError('Finish the adventure before collecting its reward.')
                p['claimed'].append(q['id'])
                p['coins'] += q['coins']
                p['xp'] += q['xp']
                message = f"Stamp collected! +{q['coins']} shells"
            elif action == 'gift':
                qty = integer(args.get('qty'),1,20)
                target = db.execute('SELECT data,seen FROM players WHERE id=?',(args.get('target'),)).fetchone()
                if target is None:
                    raise RuleError('That friend has left.')
                other = json.loads(target['data'])
                if other['id']==p['id'] or other['world']!=p['world'] or target['seen']<now-20:
                    raise RuleError('Choose another friend in this town.')
                self.near(p,(other['x'],other['y']),160)
                item = args.get('item')
                if item not in ('wood','ice','fish','berries'):
                    raise RuleError('Gifts can contain gathered resources.')
                self.spend(p,{item:qty})
                self.add(other,item,qty)
                db.execute('UPDATE players SET data=? WHERE id=?',(json.dumps(other),other['id']))
                self.stat(p,'gifts')
                message = f"Sent {qty} {ITEMS[item]['name']} to {other['name']}!"
            elif action == 'decorate':
                slot = integer(args.get('slot'),0,5)
                item = args.get('item')
                if item!='' and (item not in ITEMS or not ITEMS[item].get('decor')):
                    raise RuleError('Choose a crafted decoration.')
                if item:
                    self.spend(p,{item:1})
                if p['home'][slot]:
                    self.add(p,p['home'][slot],1)
                p['home'][slot] = item
                if item:
                    p['stats']['decorated'] = 1
                message = 'Your little corner of the world, updated.'
            elif action == 'fish-start':
                self.near(p,w['fish'])
                if p['cooldowns'].get('fishing',0)>now:
                    raise RuleError('Let the ripples settle for a moment.')
                p['fish'] = {'id':secrets.token_hex(12),'target_at':now+2.5+secrets.randbelow(1000)/1000,'world':p['world']}
                p['cooldowns']['fishing'] = now+5
                extra['challenge'] = dict(p['fish'],started_at=now,duration=5)
            elif action == 'fish-catch':
                challenge = p['fish']
                if not challenge or args.get('challenge')!=challenge['id']:
                    raise RuleError('Cast a new line first.')
                self.near(p,w['fish'])
                caught = challenge['world']==p['world'] and abs(now-challenge['target_at'])<=.45
                p['fish'] = None
                if caught:
                    self.add(p,'fish',2)
                    self.stat(p,'fish_caught')
                    p['xp'] += 10
                extra['caught'] = caught
                message = '+2 Silverfin! A beautiful catch.' if caught else 'A little early or late. The next one is yours!'
            elif action == 'emote':
                emote = args.get('emote')
                if emote not in EMOTES:
                    raise RuleError('Choose a friendly emote.')
                if p['emote_until']>now+2:
                    raise RuleError('One happy thought at a time.')
                p.update(emote=emote,emote_until=now+4)
            else:
                raise RuleError('Unknown action.')
            self.save(db,p)
            return dict(self.snapshot(db,p),message=message,**extra)
