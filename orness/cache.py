# coding: utf8
from orness import utils
import json
import redis

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db)
        

    def get(self, key):
        value = self.r.get(key)
        if value:
            try:
                # Tentative de désérialisation JSON
                return json.loads(value)
            except json.JSONDecodeError:
                # Si la valeur n'est pas au format JSON, on la retourne telle quelle
                return value
        return None

    def set(self, key, value, ex=None):
        if isinstance(value, dict) or isinstance(value, list):
            # Sérialisation JSON avant stockage
            value = json.dumps(value)
        self.r.set(key, value, ex=ex)

    def delete(self, key):
        self.r.delete(key)

    def clear(self):
        self.r.flushdb()

if __name__ == '__main__':
    rd = RedisCache()
    print(rd.get('wallets_info'))
    print("")

