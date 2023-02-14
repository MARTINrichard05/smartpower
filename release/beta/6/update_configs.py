#!/usr/bin/python
import json
path = '/etc/smartpower/'
storage = {'data': {}, 'custom_processes': {}, 'modes': {}}
with open(path + 'data.json') as json_file:
    storage['data'] = json.load(json_file)
with open(path + 'processes.json') as json_file:
    storage['processes'] = json.load(json_file)
with open(path + 'presets.json') as json_file:
    storage['modes'] = json.load(json_file)

with open(path + 'storage.json', 'w') as fp:
    json.dump(storage, fp)