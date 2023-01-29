import configparser
import os
import time

import psutil

import ryzen_ctrl as rz

max_read_retry = 10   # TOddO: IMPLEMENT SOMETHING TO PAUSE AND UNPAUSE TASKS WITH STOP SIGNAL AND COUNT SIGNAL

class Main:
    def __init__(self):
        self.data = {
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
                'timer': 0.2
            },
            'tdp': {
                'curent': 10,
                'mode': 'normal'
            }
        }
        print('initing?')
        self.config = configparser.ConfigParser()
        self.data['etc']['nbcpu'] = self.detectcpu()

        self.readcfg()
        self.readinfo('full')

        self.writecfg()

        self.main()

    def readinfo(self, mode):
        if mode == 'min':
            self.data['etc']['cpu_usage'] = psutil.cpu_percent(self.data['etc']['timer'])

        elif mode == 'full':
            self.data['etc']['cpu_usage'] = psutil.cpu_percent(self.data['etc']['timer'])
            self.data['etc']['running_cores'] = rz.getinfo('running_cores')
            for i in range(self.data['etc']['nbcpu'] + 1):
                if str(i) in self.data['etc']['running_cores']:
                    self.data['CORES'][i] = 1
                else:
                    self.data['CORES'][i] = 0
            self.data['GOVERNORS']['current'] = rz.getinfo('governor')

    def writecfg(self):
        sucess = 0
        for i in range(max_read_retry):
            try:
                with open('config.ini', 'w') as configfile:
                    self.config.write(configfile)
            except:
                break
        else:
            sucess = 1

        if sucess == 0:
            print("error reading cfg file")
            exit(1)
        else:
            sucess = 0

    def detectcpu(self):
        cpufolder = '/sys/devices/system/cpu/'
        cpunb = 0  # not starting from 1 but 0
        while True:
            if os.path.isdir(cpufolder + 'cpu' + str(cpunb + 1)):
                cpunb += 1
            else:
                return cpunb

    def readcfg(self):
        sucess = 0
        for i in range(max_read_retry):
            try:
                self.config.read('config.ini')
            except:
                break
        else:
            sucess = 1

        if sucess == 0:
            print("error reading cfg file")
            exit(1)
        else:
            sucess = 0

    def managetdp(self):   # sudo ryzenadj -a 50000 -c 50000 -b 50000 -g 40000 -k 100000
        if self.data['tdp']['mode'] == 'normal': # data = [(int(p), c) for p, c in [x.rstrip('\n').split(' ', 1) for x in os.popen('ps h -eo pid:1,command')]]
            pass
        elif self.data['tdp']['mode'] == 'turbo':
            rz.set('tdp', int(self.config['CONFIG']['max_tdp']))

    def managecpucores(self, mode):
        if mode == '-':
            for i in range(self.data['etc']['nbcpu'] - int(self.config['CONFIG']['min_active_cores']) + 1):
                if self.data['CORES'][self.data['etc']['nbcpu'] - i] == 1:
                    self.data['CORES'][self.data['etc']['nbcpu'] - i] = 0
                    rz.corestate(self.data['etc']['nbcpu'] - i, 0)
                    print("core " + str(self.data['etc']['nbcpu'] - i + 1) + " offline")
                    break
        elif mode == '+':
            for i in range(self.data['etc']['nbcpu'] + 1):
                if self.data['CORES'][i] == 0:
                    self.data['CORES'][i] = 1
                    rz.corestate(i, 1)
                    print("core " + str(i + 1) + " online")
                    break

    def main(self):
        self.readinfo('full')

        print("main starting")
        print('nbcpu : ' + str(self.data['etc']['nbcpu']))

        while True:
            self.readinfo('min')

            if self.data['etc']['cpu_usage'] < int(self.config['CONFIG']['low_usage']):
                if self.data['CORES'][int(self.config['CONFIG']['min_active_cores'])] == 0:
                    self.data['etc']['timer'] = 0.4
                else:
                    self.data['etc']['timer'] = 0.05
                    self.managecpucores('-')
            elif self.data['etc']['cpu_usage'] > int(self.config['CONFIG']['high_usage']):
                self.data['etc']['timer'] = 0.03
                self.managecpucores('+')
            else:
                self.data['etc']['timer'] = 0.2

            time.sleep(self.data['etc']['timer'])


if __name__ == '__main__':
    worker = Main()
    print("done")
