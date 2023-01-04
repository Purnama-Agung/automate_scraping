import json
import random

from src import PROXY_PATH

def get_proxy(files):
    try:
        with open('{}/{}'.format(PROXY_PATH, files), 'r') as f:
            proxies = f.read()
            proxies = json.loads(proxies)
            f.close()

        items = random.choice(proxies)
        address = items['address']
        port = int(items['port'])
        proxy = {'address': address, 'port': port}
    except:
        raise
    return proxy
