import json

data = {
    'CORES': {
        1: 1
    },
    'GOVERNORS': {
        'conservative': True,
        'powersave': True,
        'performance': True,
        'current': 'conservative'
    },
    'etc': {
        'cpu_usage': 0.0,
        'timer': 0.2,
        'modelist': ['normal', 'turbo', 'silent', 'eco', 'manual'],
        'mode': 'normal',
        'ratios': {
            'eco': 0.85,
            'silent': 0.85,
            'turbo': 1.25,
        }
    },
    'tdp': {
        'current': 10000,
        'list': []
    },
    'tmp': {
        'current': 65,
        'list': []
    },
    'other_config': {
        'min_tdp': 4000,
        'max_tdp': 35000,
        'max_temp': 99,
        'high_usage': 70,
        'low_usage': 20,
        'min_active_cores': 2
    },
    'manual':{
        'tdp': 10000,
        'tmp': 70
    }
}

with open('data.json', 'w') as fp:
    json.dump(data, fp)
