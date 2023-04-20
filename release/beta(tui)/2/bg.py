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
        self.storage = {'data': {}, 'custom_processes': {}, 'modes': {}}
        self.path = str(pathlib.Path(__file__).parent.resolve()) + '/'
        self.readcfg()
        self.listener = Listener((self.storage['listener']['connection']['adress'],self.storage['listener']['connection']['port']), authkey=bytes(self.storage['listener']['connection']['authkey'], 'ascii'))
        self.storage['data']['etc']['nbcpu'] = self.detectcpu()

        self.readinfo('full')

        self.writecfg()

        self.main()

    def readinfo(self, mode):
        if mode == 'min':
            self.storage['data']['etc']['cpu_usage'] = psutil.cpu_percent(self.storage['data']['etc']['timer'])

        elif mode == 'full':
            self.storage['data']['etc']['cpu_usage'] = psutil.cpu_percent(self.storage['data']['etc']['timer'])
            self.storage['data']['etc']['running_cores'] = rz.getinfo('running_cores')
            for i in range(self.storage['data']['etc']['nbcpu'] + 1):
                if str(i) in self.storage['data']['etc']['running_cores']:
                    self.storage['data']['CORES'][i] = 1
                else:
                    self.storage['data']['CORES'][i] = 0
            self.storage['data']['GOVERNORS']['current'] = rz.getinfo('governor')

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
                            if tempdata[1] in self.storage['modes']:
                                self.storage['data']['etc']['mode'] = tempdata[1]
                                self.writecfg()
                                conn.send('200')
                            else:
                                conn.send('404')
                        elif tempdata[0] == 'ratio':
                            if tempdata[1] in self.storage['data']['etc']['modelist']:
                                self.storage['data']['etc']['ratios'][tempdata[1]] = tempdata[2]
                                self.writecfg()
                                conn.send('200')
                        elif tempdata[0] == 'manual':
                            if tempdata[1] == 'tdp':
                                self.storage['data']['manual']['tdp'] = tempdata[2]
                                self.writecfg()
                                conn.send('200')
                            elif tempdata[1] == 'temp':
                                self.storage['data']['manual']['tmp'] = tempdata[2]
                                self.writecfg()
                                conn.send('200')
                        elif tempdata[0] == 'add_proc':
                            conn.send('ready')
                            proc = conn.recv()
                            conn.send('ready2')
                            tdp = conn.recv()
                            conn.send('ready3')
                            tmp = conn.recv()
                            self.storage['processes'][str(proc)] = {'tdp': int(tdp), 'tmp': int(tmp)}
                            conn.send(self.storage['processes'])
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
                                self.storage['modes'][str(name)] = {'tdpr': float(tdpr), 'tmpr': float(tmpr),'max_tdp': int(max_tdp), 'max_tmp': int(max_tmp),'min_tdp': int(min_tdp), 'min_tmp': int(min_tmp),}
                                conn.send(self.storage['modes'])
                                self.writecfg()
                            except Exception as e:
                                conn.send(e)
                        elif tempdata[0] == 'state':
                            conn.send(self.storage)
                        elif tempdata[0] == 'ryzenadj':
                            conn.send(rz.ryzenadj_info())
                        elif tempdata[0] == 'edit': # edit (name of the preset) (what to edit) (value)
                            if tempdata[1] in self.storage['modes']:
                                if tempdata[2] in self.storage['modes'][tempdata[1]]:
                                    self.storage['modes'][tempdata[1]][tempdata[2]] = tempdata[3]
                                    self.writecfg()
                                    conn.send('200')
                                elif tempdata[2] == 'name':
                                    temp = self.storage['modes'][tempdata[1]]
                                    self.storage['modes'].pop(tempdata[1])
                                    self.storage['modes'][tempdata[3]] = temp
                                    self.writecfg()
                                    conn.send('200')
                                else :
                                    conn.send('404')
                            else:
                                conn.send('404')
                        elif tempdata[0] == 'delete':
                            if tempdata[1] in self.storage['modes']:
                                self.storage['modes'].pop(tempdata[1])
                                self.writecfg()
                                conn.send('200')
                            else:
                                conn.send('404')
                        elif tempdata[0] == 'change_key':
                            self.storage['listener']['connection']['authkey'] = tempdata[1]
                            self.writecfg()
                            conn.send(self.storage['listener']['connection']['authkey'])

                self.listener.close()
            except:
                pass

    def writecfg(self):
        with open(self.path + 'storage.json', 'w') as fp:
            json.dump(self.storage, fp)

    def detectcpu(self):
        cpufolder = '/sys/devices/system/cpu/'
        cpunb = 0  # not starting from 1 but 0
        while True:
            if os.path.isdir(cpufolder + 'cpu' + str(cpunb + 1)):
                cpunb += 1
            else:
                return cpunb

    def readcfg(self):
        with open(self.path + 'storage.json') as json_file:
            self.storage = json.load(json_file)

    def managetdp(self):  # sudo ryzenadj -a 50000 -c 50000 -b 50000 -g 40000 -k 100000
        self.storage['data']['tdp']['list'].sort(reverse=True)
        current = int(int(self.storage['data']['tdp']['list'][0]) * float(self.storage['modes'][str(self.storage['data']['etc']['mode'])]['tdpr']))
        if current == self.storage['data']['tdp']['current']:
            pass
        else:
            if current < int(self.storage['modes'][str(self.storage['data']['etc']['mode'])]['min_tdp']):
                self.storage['data']['tdp']['current'] = int(self.storage['modes'][str(self.storage['data']['etc']['mode'])]['min_tdp'])
                rz.set('tdp', int(self.storage['data']['tdp']['current']))
            elif current > int(self.storage['modes'][str(self.storage['data']['etc']['mode'])]['max_tdp']):
                self.storage['data']['tdp']['current'] = int(self.storage['modes'][str(self.storage['data']['etc']['mode'])]['max_tdp'])
                rz.set('tdp', int(self.storage['data']['tdp']['current']))
            else:
                self.storage['data']['tdp']['current'] = current
                rz.set('tdp', int(self.storage['data']['tdp']['current']))

    def managetmp(self):
        self.storage['data']['tmp']['list'].sort(reverse=True)
        current = int(self.storage['data']['tmp']['list'][0]) * float(self.storage['modes'][str(self.storage['data']['etc']['mode'])]['tmpr'])
        if current < int(self.storage['modes'][str(self.storage['data']['etc']['mode'])]['min_tmp']):
            current = int(self.storage['modes'][str(self.storage['data']['etc']['mode'])]['min_tmp'])
        elif current > int(self.storage['modes'][str(self.storage['data']['etc']['mode'])]['max_tmp']):
            current = int(self.storage['modes'][str(self.storage['data']['etc']['mode'])]['max_tmp'])
        if current == self.storage['data']['tmp']['current']:
            pass
        else:
            self.storage['data']['tmp']['current'] = current
            rz.set('temp', int(self.storage['data']['tmp']['current']))

    def refreshprocess(self):
        processes = [(int(p), c) for p, c in [x.rstrip('\n').split(' ', 1) for x in os.popen('ps h -eo pid:1,command')]]
        tdplist = []
        tmplist = []
        coreslist = []
        for i in range(len(processes)):  # will create a list of the different tdps
            if str(processes[i][1]) in self.storage['processes']:
                tdplist.append(self.storage['processes'][processes[i][1]]['tdp'])
                tmplist.append(self.storage['processes'][processes[i][1]]['tmp'])
                try:
                    coreslist.append(self.storage['processes'][processes[i][1]]['min_active_cores'])
                except:
                    pass

        self.storage['data']['tdp']['list'] = tdplist
        self.storage['data']['tmp']['list'] = tmplist
        coreslist.sort(reverse=True)
        try:
            self.storage['data']['other_config']['min_active_cores'] = coreslist[0]
        except:
            pass

    def smartcoefs(self):
        pass

    def managecpucores(self, mode):
        if self.storage['data']['CORES'][self.storage['data']['other_config']['min_active_cores'] - 1] == 0:
            for i in range(self.storage['data']['other_config']['min_active_cores']):
                if self.storage['data']['CORES'][i] == 0:
                    self.storage['data']['CORES'][i] = 1
                    rz.corestate(i, 1)
                    print("core " + str(i + 1) + " online")

        elif mode == '-':
            for i in range(self.storage['data']['etc']['nbcpu'] - int(self.storage['data']['other_config']['min_active_cores']) + 1):
                if self.storage['data']['CORES'][self.storage['data']['etc']['nbcpu'] - i] == 1:
                    self.storage['data']['CORES'][self.storage['data']['etc']['nbcpu'] - i] = 0
                    rz.corestate(self.storage['data']['etc']['nbcpu'] - i, 0)
                    print("core " + str(self.storage['data']['etc']['nbcpu'] - i + 1) + " offline")
                    break
        if mode == '+':
            for i in range(self.storage['data']['etc']['nbcpu'] + 1):
                if self.storage['data']['CORES'][i] == 0:
                    self.storage['data']['CORES'][i] = 1
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

            if self.storage['data']['etc']['cpu_usage'] < int(self.storage['data']['other_config']['low_usage']):
                if self.storage['data']['CORES'][int(self.storage['data']['other_config']['min_active_cores'])] == 0:
                    self.storage['data']['etc']['timer'] = 0.4
                else:
                    self.storage['data']['etc']['timer'] = 0.05
                    self.managecpucores('-')
            elif self.storage['data']['etc']['cpu_usage'] > int(self.storage['data']['other_config']['high_usage']):
                self.storage['data']['etc']['timer'] = 0.03
                self.managecpucores('+')
            else:
                self.storage['data']['etc']['timer'] = 0.2
            time.sleep(self.storage['data']['etc']['timer'])
    def suspend(self):
         while True:
             before = time.time()
             time.sleep(10)
             after = time.time()
             if (after - before) > 12:
                print("sleeped")
                rz.set('temp', int(self.storage['data']['tmp']['current']))
                rz.set('tdp', int(self.storage['data']['tdp']['current']))
             rz.set('temp', int(self.storage['data']['tmp']['current']))
             rz.set('tdp', int(self.storage['data']['tdp']['current']))


    def main(self):
        self.readinfo('full')
        if self.storage['data']['other_config']['disable_cores'] == True:
            core_thread = Thread(target=self.cores)
        other_thread = Thread(target=self.tdptmp)
        socket_thread = Thread(target=self.socket)
        suspend_thread = Thread(target=self.suspend)

        if self.storage['data']['other_config']['disable_cores'] == True:
            core_thread.start()
        other_thread.start()
        socket_thread.start()
        suspend_thread.start()
        print('running')
        if self.storage['data']['other_config']['disable_cores'] == True:
            core_thread.join()
        other_thread.join()
        socket_thread.join()
        suspend_thread.join()


if __name__ == '__main__':
    worker = Main()
    print("done")
