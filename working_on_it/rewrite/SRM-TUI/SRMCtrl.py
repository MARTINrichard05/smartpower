#!/usr/bin/python

import sys
from multiprocessing.connection import Client
import subprocess
import json

user = subprocess.check_output(['whoami'], shell=True,  text=True).split('\n')[0]
path = '/home/'+user+'/.config/SmartRyzenManager/'


class SRMCtrl:
    def __init__(self):
        pass

    def readConfig(self):
        try:
            with open('config.json', 'r') as json_file:
                data = json.load(json_file)
                self.cfg = data
        except FileNotFoundError:
            self.cfg = {
                "adress": 'localhost',
                "port": 9899,
                "authkey": 'default'
            }
            with open('config.json', 'w') as outfile:
                json.dump(self.cfg, outfile)
    def send(self):
        args = sys.argv
        args.pop(0)
        self.conn = Client((self.cfg['adress'], self.cfg['port']), authkey=bytes(self.cfg['authkey'], 'utf-8'))
        self.conn.send(args)
        while True:
            data = self.conn.recv()
            if data == 'exit':
                self.conn.close()
                break
            else:
                print(data)

if __name__ == '__main__':
    srm = SRMCtrl()
    srm.readConfig()
    srm.send()