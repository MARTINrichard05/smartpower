import configparser
import os
import ryzen_ctrl as rz
import psutil
import time

max_read_retry = 10


class Main:
    def __init__(self):
        print('initing?')
        self.config = configparser.ConfigParser()
        self.nbcpu = self.detectcpu()

        self.readcfg()
        if self.config['STATE']['first_run'] == '1':
            self.readinfo('full')

            govs = rz.getinfo('governors')
            for i in range(len(govs)):
                if govs[i] in self.config['GOVERNORS']:
                    self.config['GOVERNORS'][govs[i]] = '1'

            self.config['STATE']['first_run'] = '0'
            self.writecfg()

        self.main()

    def readinfo(self,mode):
        if mode == 'min':
            self.config['STATE']['cpu_usage'] = str(psutil.cpu_percent(0.1))

        elif mode == 'full':
            self.config['STATE']['cpu_usage'] = str(psutil.cpu_percent(0.1))
            self.running_cores = rz.getinfo('running_cores')
            for i in range(self.nbcpu+1):
                if str(i) in self.running_cores:
                    self.config['CORES'][str(i)] = '1'
                else:
                    self.config['CORES'][str(i)] = '0'
            self.config['GOVERNORS']['current'] = rz.getinfo('governor')

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
        cpunb = 0 #not starting from 1 but 0
        while True:
            if os.path.isdir(cpufolder + 'cpu' + str(cpunb + 1)):
                cpunb += 1
            else:
                return cpunb


    def readcfg(self):
        sucess = 0
        for i in range(max_read_retry):
            try :
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

    def managecpucores(self):
        if float(self.config['STATE']['cpu_usage']) < int(self.config['CONFIG']['low_usage']) :
            for i in range(self.nbcpu - int(self.config['CONFIG']['min_active_cores']) + 1):
                if self.config['CORES'][str(self.nbcpu - i)] == str(1):
                    self.config['CORES'][str(self.nbcpu - i)] = str(0)
                    rz.corestate(self.nbcpu - i, 0)
                    print("core " + str(self.nbcpu -i) + "offline")
                    break
        elif float(self.config['STATE']['cpu_usage']) > int(self.config['CONFIG']['high_usage']) :
            for i in range(self.nbcpu+1):
                if self.config['CORES'][str(i)] == str(0):
                    self.config['CORES'][str(i)] = str(1)
                    rz.corestate(i, 1)
                    print("core " + str(i) + "online")
                    break

    def main(self):
        self.readinfo('full')
        self.managecpucores()

        print("main starting")
        print(self.nbcpu)

        while True:
            self.readinfo('min')
            self.managecpucores()
            time.sleep(0.1)




if __name__ == '__main__':
    worker = Main()
    print("done")
