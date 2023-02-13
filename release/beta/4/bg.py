import os
import time
from multiprocessing.connection import Listener
import json
import pathlib
import psutil
import ryzen_ctrl as rz
from threading import Thread

address = ('localhost', 6000)

max_read_retry = 10  # TOddo: IMPLEMENT SOMETHING TO PAUSE AND UNPAUSE TASKS WITH STOP SIGNAL AND COUNT SIGNAL


class Main:
    def __init__(self):
        self.data = {}
        self.listener = Listener(address, authkey=b'eogn68rb8r69')
        self.path = str(pathlib.Path(__file__).parent.resolve()) + '/'
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

    def socket(self):  # m for mode (powersave
        print('listening')
        while True:
            try:
                conn = self.listener.accept()
                while True:
                    msg = conn.recv()

                    # do something with msg
                    if msg == 'close':
                        conn.close()
                        break
                    else:
                        tempdata = msg.split(' ')
                        if tempdata[0] == 'mode':
                            if tempdata[1] in self.modes:
                                self.data['etc']['mode'] = tempdata[1]
                                self.writecfg()
                                conn.send('200')
                            else:
                                conn.send('404')
                        elif tempdata[0] == 'ratio':
                            if tempdata[1] in self.data['etc']['modelist']:
                                self.data['etc']['ratios'][tempdata[1]] = tempdata[2]
                                self.writecfg()
                                conn.send('200')
                        elif tempdata[0] == 'manual':
                            if tempdata[1] == 'tdp':
                                self.data['manual']['tdp'] = tempdata[2]
                                self.writecfg()
                                conn.send('200')
                            elif tempdata[1] == 'temp':
                                self.data['manual']['tmp'] = tempdata[2]
                                self.writecfg()
                                conn.send('200')
                        elif tempdata[0] == 'add_proc':
                            conn.send('ready')
                            proc = conn.recv()
                            conn.send('ready2')
                            tdp = conn.recv()
                            conn.send('ready3')
                            tmp = conn.recv()
                            self.custom_processes[str(proc)] = {'tdp': int(tdp), 'tmp': int(tmp)}
                            conn.send(self.custom_processes)
                            self.writecfg()
                        elif tempdata[0] == 'add_mode':
                            try:
                                conn.send('ready')
                                name = conn.recv()
                                conn.send('ready1')
                                tdpr = conn.recv()
                                conn.send('ready2')
                                tmpr = conn.recv()
                                conn.send('ready3')
                                max_tdp = conn.recv()
                                conn.send('ready4')
                                max_tmp = conn.recv()
                                conn.send('ready5')
                                min_tdp = conn.recv()
                                conn.send('ready6')
                                min_tmp = conn.recv()
                                self.modes[str(name)] = {'tdpr': float(tdpr), 'tmpr': float(tmpr),'max_tdp': int(max_tdp), 'max_tmp': int(max_tmp),'min_tdp': int(min_tdp), 'min_tmp': int(min_tmp),}
                                conn.send(self.modes)
                                self.writecfg()
                            except Exception as e:
                                conn.send(e)
                        elif tempdata[0] == 'state':
                            conn.send(self.data)

                self.listener.close()
            except:
                pass

    def writecfg(self):
        with open(self.path + 'data.json', 'w') as fp:
            json.dump(self.data, fp)
        with open(self.path + 'processes.json', 'w') as fp:
            json.dump(self.custom_processes, fp)
        with open(self.path + 'presets.json', 'w') as fp:
            json.dump(self.modes, fp)

    def detectcpu(self):
        cpufolder = '/sys/devices/system/cpu/'
        cpunb = 0  # not starting from 1 but 0
        while True:
            if os.path.isdir(cpufolder + 'cpu' + str(cpunb + 1)):
                cpunb += 1
            else:
                return cpunb

    def readcfg(self):
        with open(self.path + 'data.json') as json_file:
            self.data = json.load(json_file)
        with open(self.path + 'processes.json') as json_file:
            self.custom_processes = json.load(json_file)
        with open(self.path + 'presets.json') as json_file:
            self.modes = json.load(json_file)

    def managetdp(self):  # sudo ryzenadj -a 50000 -c 50000 -b 50000 -g 40000 -k 100000
        self.data['tdp']['list'].sort(reverse=True)
        current = int(int(self.data['tdp']['list'][0]) * float(self.modes[str(self.data['etc']['mode'])]['tdpr']))
        if current == self.data['tdp']['current']:
            pass
        else:
            if current < int(self.modes[str(self.data['etc']['mode'])]['min_tdp']):
                self.data['tdp']['current'] = int(self.modes[str(self.data['etc']['mode'])]['min_tdp'])
                rz.set('tdp', int(self.data['tdp']['current']))
            elif current > int(self.modes[str(self.data['etc']['mode'])]['max_tdp']):
                self.data['tdp']['current'] = int(self.modes[str(self.data['etc']['mode'])]['max_tdp'])
                rz.set('tdp', int(self.data['tdp']['current']))
            else:
                self.data['tdp']['current'] = current
                rz.set('tdp', int(self.data['tdp']['current']))

    def managetmp(self):
        self.data['tmp']['list'].sort(reverse=True)
        current = int(self.data['tmp']['list'][0]) * float(self.modes[str(self.data['etc']['mode'])]['tmpr'])
        if current == self.data['tmp']['current']:
            pass
        else:
            if current < int(self.modes[str(self.data['etc']['mode'])]['min_tmp']):
                self.data['tmp']['current'] = int(self.modes[str(self.data['etc']['mode'])]['min_tmp'])
                rz.set('temp', int(self.data['tmp']['current']))
            elif current > int(self.modes[str(self.data['etc']['mode'])]['max_tmp']):
                self.data['tmp']['current'] = int(self.modes[str(self.data['etc']['mode'])]['max_tmp'])
                rz.set('temp', int(self.data['tmp']['current']))
            else:
                self.data['tmp']['current'] = current
                rz.set('temp', int(self.data['tmp']['current']))

    def refreshprocess(self):
        processes = [(int(p), c) for p, c in [x.rstrip('\n').split(' ', 1) for x in os.popen('ps h -eo pid:1,command')]]
        tdplist = []
        tmplist = []
        coreslist = []
        for i in range(len(processes)):  # will create a list of the different tdps
            if str(processes[i][1]) in self.custom_processes:
                tdplist.append(self.custom_processes[processes[i][1]]['tdp'])
                tmplist.append(self.custom_processes[processes[i][1]]['tmp'])
                try:
                    coreslist.append(self.custom_processes[processes[i][1]]['min_active_cores'])
                except:
                    pass

        self.data['tdp']['list'] = tdplist
        self.data['tmp']['list'] = tmplist
        coreslist.sort(reverse=True)
        try:
            self.data['other_config']['min_active_cores'] = coreslist[0]
        except:
            pass

    def smartcoefs(self):
        pass

    def managecpucores(self, mode):
        if self.data['CORES'][self.data['other_config']['min_active_cores'] - 1] == 0:
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
        print('managing tdp/tmp')
        while True:
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
        print('running')
        if self.data['other_config']['disable_cores'] == True:
            core_thread.join()
        other_thread.join()
        socket_thread.join()


if __name__ == '__main__':
    worker = Main()
    print("done")
