#!/usr/bin/python
import json
path = '/etc/smartpower/'
try :
    with open(path + 'storage.json') as json_file:
        storage = json.load(json_file)
    print('newer version, adding listener data')
    storage['listener'] = {'connection': {'adress': 'localhost', 'port': 6000, 'authkey': 'eogn68rb8r69'}, }
except:
    storage = {'data': {}, 'custom_processes': {}, 'modes': {}}
    with open(path + 'data.json') as json_file:
        storage['data'] = json.load(json_file)
    with open(path + 'processes.json') as json_file:
        storage['processes'] = json.load(json_file)
    with open(path + 'presets.json') as json_file:
        storage['modes'] = json.load(json_file)

with open(path + 'storage.json', 'w') as fp:
    json.dump(storage, fp)