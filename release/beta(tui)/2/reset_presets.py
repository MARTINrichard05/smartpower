import json
import pathlib
path = str(pathlib.Path(__file__).parent.resolve())+'/'
presets = {
    'normal' : {'tdpr' : 1, 'tmpr' : 1, 'max_tdp' : 25000, 'max_tmp' : 80, 'min_tdp' : 6500, 'min_tmp' : 65,},
    'eco' : {'tdpr' : 0.85, 'tmpr' : 1, 'max_tdp' : 12000, 'max_tmp' : 80, 'min_tdp' : 5000, 'min_tmp' : 65,},
    'silent' : {'tdpr' : 1, 'tmpr' : 0.85, 'max_tdp' : 25000, 'max_tmp' : 74, 'min_tdp' : 6500, 'min_tmp' : 65,},
    'turbo' : {'tdpr' : 1.2, 'tmpr' : 1.2, 'max_tdp' : 35000, 'max_tmp' : 95, 'min_tdp' : 15000, 'min_tmp' : 75,},
}
with open(path + 'presets.json', 'w') as fp:
    json.dump(presets, fp)