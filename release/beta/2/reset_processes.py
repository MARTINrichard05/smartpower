import json

data = {
    '/usr/lib/systemd/systemd-machined' : {
        'tmp': 70,
        'tdp': 10000,
        'min_active_cores': 1
    }
}

with open('processes.json', 'w') as fp:
    json.dump(data, fp)
