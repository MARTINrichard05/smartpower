import os
import time
import processes_list
from multiprocessing.connection import Listener
import json

address = ('localhost', 6000)


import psutil

import ryzen_ctrl as rz
from threading import Thread

max_read_retry = 10   # TOddo: IMPLEMENT SOMETHING TO PAUSE AND UNPAUSE TASKS WITH STOP SIGNAL AND COUNT SIGNAL

class Main:
    def __init__(self):
        self.data = {}
        print('initing?')
        self.listener = Listener(address, authkey=b'eogn68rb8r69')
        self.readcfg()
        self.data['etc']['nbcpu'] = self.detectcpu()

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

    def socket(self): # m for mode (powersave
        while True:
            try :
                conn = self.listener.accept()
                print('new connection')
                while True:
                    msg = conn.recv()

                    # do something with msg
                    if msg == 'close':
                        conn.close()
                        break
                    else :
                        tempdata = msg.split(' ')
                        if tempdata[0] == 'mode':
                            if tempdata[1] in self.data['etc']['modelist']:
                                print('found mode')
                                self.data['etc']['mode'] = tempdata[1]
                                self.writecfg()
                        elif tempdata[0] == 'ratio' :
                            if tempdata[1] in self.data['etc']['modelist']:
                                self.data['etc']['ratios'][tempdata[1]] = tempdata[2]
                                self.writecfg()
                        elif tempdata[0] == 'manual':
                            if tempdata[1] == 'tdp':
                                self.data['manual']['tdp'] = tempdata[2]
                                self.writecfg()
                            elif tempdata[1] == 'temp':
                                self.data['manual']['tmp'] = tempdata[2]
                                self.writecfg()


                self.listener.close()
            except :
                pass

    def writecfg(self):
        import json

        with open('data.json', 'w') as fp:
            json.dump(self.data, fp)

    def detectcpu(self):
        cpufolder = '/sys/devices/system/cpu/'
        cpunb = 0  # not starting from 1 but 0
        while True:
            if os.path.isdir(cpufolder + 'cpu' + str(cpunb + 1)):
                cpunb += 1
            else:
                return cpunb

    def readcfg(self):
        with open('data.json') as json_file:
            data = json.load(json_file)
            self.data = data

    def managetdp(self):   # sudo ryzenadj -a 50000 -c 50000 -b 50000 -g 40000 -k 100000
        if self.data['etc']['mode'] == 'normal' or self.data['etc']['mode'] == 'silent': # data = [(int(p), c) for p, c in [x.rstrip('\n').split(' ', 1) for x in os.popen('ps h -eo pid:1,command')]]

            self.data['tdp']['list'].sort(reverse=True)

            if int(self.data['tdp']['list'][0]) == self.data['tdp']['current']:
                pass

            else :
                self.data['tdp']['current'] = int(self.data['tdp']['list'][0])
                rz.set('tdp', int(self.data['tdp']['current']))

        elif self.data['etc']['mode'] == 'turbo':

            if int(self.data['other_config']['max_tdp']) == self.data['tdp']['current']:
                pass
            else:
                self.data['tdp']['current'] = int(self.data['other_config']['max_tdp'])
                rz.set('tdp', int(self.data['other_config']['max_tdp']))
        elif self.data['etc']['mode'] == 'eco':

            self.data['tdp']['list'].sort(reverse=True)
            tmp = float(self.data['tdp']['list'][0]) * float(self.data['etc']['ratios']['eco'])
            if int(tmp) == self.data['tmp']['current']:
                pass
            else:
                self.data['tdp']['current'] = int(tmp)
                rz.set('tdp', int(self.data['tdp']['current']))
        elif self.data['etc']['mode'] == 'manual':
            if int(self.data['manual']['tdp']) == self.data['tdp']['current']:
                pass
            else:
                self.data['tdp']['current'] = int(self.data['manual']['tdp'])
                rz.set('tdp', int(self.data['tdp']['current']))
    def managetmp(self):
        if self.data['etc']['mode'] == 'normal' or self.data['etc']['mode'] == 'eco':  # data = [(int(p), c) for p, c in [x.rstrip('\n').split(' ', 1) for x in os.popen('ps h -eo pid:1,command')]]
            self.data['tmp']['list'].sort(reverse=True)
            if int(self.data['tmp']['list'][0]) == self.data['tmp']['current']:
                pass
            else:
                self.data['tmp']['current'] = int(self.data['tmp']['list'][0])
                rz.set('temp', int(self.data['tmp']['current']))
        
        elif self.data['etc']['mode'] == 'turbo':

            if int(self.data['other_config']['max_temp']) == self.data['tmp']['current']:
                pass
            else :
                self.data['tmp']['current'] = int(self.data['other_config']['max_temp'])
                rz.set('temp', int(self.data['other_config']['max_temp']))

        elif self.data['etc']['mode'] == 'silent':

            self.data['tmp']['list'].sort(reverse=True)
            tmp = float(self.data['tmp']['list'][0]) * float(self.data['etc']['ratios']['silent'])
            if int(tmp) == self.data['tmp']['current']:
                pass
            else:
                self.data['tmp']['current'] = int(tmp)
                rz.set('temp', int(self.data['tmp']['current']))
        elif self.data['etc']['mode'] == 'manual':
            if int(self.data['manual']['tmp']) == self.data['tmp']['current']:
                pass
            else:
                self.data['tmp']['current'] = int(self.data['manual']['tmp'])
                rz.set('tmp', int(self.data['tmp']['current']))

    def refreshprocess(self):
        processes = [(int(p), c) for p, c in [x.rstrip('\n').split(' ', 1) for x in os.popen('ps h -eo pid:1,command')]]
        tdplist = []
        tmplist = []
        coreslist = []
        for i in range(len(processes)): # will create a list of the different tdps
            if str(processes[i][1]) in processes_list.custom_processes:
                tdplist.append(processes_list.custom_processes[processes[i][1]]['tdp'])
                tmplist.append(processes_list.custom_processes[processes[i][1]]['tmp'])
                coreslist.append(processes_list.custom_processes[processes[i][1]]['min_active_cores'])

        self.data['tdp']['list'] = tdplist
        self.data['tmp']['list'] = tmplist
        coreslist.sort(reverse=True)
        self.data['other_config']['min_active_cores'] = coreslist[0]

    def managecpucores(self, mode):
        if self.data['CORES'][self.data['other_config']['min_active_cores']-1] == 0:
            for i in range(self.data['other_config']['min_active_cores']):
                if self.data['CORES'][i] == 0:
                    self.data['CORES'][i] = 1
                    rz.corestate(i, 1)
                    print("core " + str(i + 1) + " online")

        elif mode == '-':
            for i in range(self.data['etc']['nbcpu'] - int(self.data['other_config']['min_active_cores']) + 1):
                if self.data['CORES'][self.data['etc']['nbcpu'] - i] == 1:
                    self.data['CORES'][self.data['etc']['nbcpu'] - i] = 0
                    rz.corestate(self.data['etc']['nbcpu'] - i, 0)
                    print("core " + str(self.data['etc']['nbcpu'] - i + 1) + " offline")
                    break
        if mode == '+':
            for i in range(self.data['etc']['nbcpu'] + 1):
                if self.data['CORES'][i] == 0:
                    self.data['CORES'][i] = 1
                    rz.corestate(i, 1)
                    print("core " + str(i + 1) + " online")
                    break
    def tdptmp(self):
        while True:
            if self.data['etc']['mode'] == 'normal' or self.data['etc']['mode'] == 'powersave' or self.data['etc']['mode'] == 'silent' or self.data['etc']['mode'] == 'turbo':
                self.refreshprocess()
            self.managetmp()
            self.managetdp()
            time.sleep(2)
    def cores(self):
        while True:
            self.readinfo('min')

            if self.data['etc']['cpu_usage'] < int(self.data['other_config']['low_usage']):
                if self.data['CORES'][int(self.data['other_config']['min_active_cores'])] == 0:
                    self.data['etc']['timer'] = 0.4
                else:
                    self.data['etc']['timer'] = 0.05
                    self.managecpucores('-')
            elif self.data['etc']['cpu_usage'] > int(self.data['other_config']['high_usage']):
                self.data['etc']['timer'] = 0.03
                self.managecpucores('+')
            else:
                self.data['etc']['timer'] = 0.2
            time.sleep(self.data['etc']['timer'])

    def main(self):
        self.readinfo('full')
        if self.data['other_config']['disable_cores'] == True:
            core_thread = Thread(target=self.cores)
        other_thread = Thread(target=self.tdptmp)
        socket_thread = Thread(target=self.socket)

        if self.data['other_config']['disable_cores'] == True:
            core_thread.start()
        other_thread.start()
        socket_thread.start()
        if self.data['other_config']['disable_cores'] == True:
            core_thread.join()
        other_thread.join()
        socket_thread.join()



if __name__ == '__main__':
    worker = Main()
    print("done")
