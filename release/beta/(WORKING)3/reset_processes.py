import json

data = {
    '/usr/lib/systemd/systemd-machined' : {
        'tmp': 70,
        'tdp': 10000,
        'min_active_cores': 1
    }
}

data['wtf'] = 'omg'

with open('processes.json', 'w') as fp:
    json.dump(data, fp)
