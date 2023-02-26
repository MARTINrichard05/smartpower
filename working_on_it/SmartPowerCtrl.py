#!/usr/bin/python
from multiprocessing.connection import Client
import os
import sys
import time
import json
import pathlib
import subprocess

user = subprocess.check_output(['whoami'], shell=True,  text=True).split('\n')[0]
path = '/home/'+user+'/.config/smartpower/'
storage = {}

def readcfg():
    with open(path + 'storage-ctrl.json') as json_file:
        return json.load(json_file)


def writecfg(storage2):
    with open(path + 'storage-ctrl.json', 'w') as fp:
        json.dump(storage2, fp)
try :
    storage = readcfg()
except:
    print('creating config file')
    storage = {'connection' : {'adress': 'localhost', 'port' : 6000, 'authkey' : 'eogn68rb8r69'},}
    os.system('mkdir ~/.config/smartpower')
    writecfg(storage)

conn = Client((storage['connection']['adress'], storage['connection']['port']), authkey=bytes(storage['connection']['authkey'], 'ascii'))

command = sys.argv
if len(command) > 1 :
    if command[1] == 'help':
        print('A way to interact without root privileges with my smartpower daemon')
        print(' list of commands available:')
        print('mode      : use mode + arg to set it')
        print('       turbo  : turn all up to get maximum power (all *ratio , up to the cap)')
        print('       normal : working normally as in config files and the process list')
        print('       eco    : turn tdp down by the wanted ratio but keep temps normals')
        print('       silent : turn down max temp by the wanted ratio to be silent')
        print('       manual : you can can manually set the params')
        print('ratio     : set the desired ratio for modes:')
        print('       syntax : [mode] [ratio]')
        print('list_proc : list actives processes , so you can copy the name and use it into the add_proc command')
        print('add_proc  : add a process to the list to be used')
        print('       syntax : add_proc [process] [tdp(mW)] [max temp(°C)]')
        print('add_mode  : add a preset/mode to the list')
        print('       syntax : add_mode [mode_name] [tdp ratio] [temp ratio] [max tdp] [max temp] [min tdp] [min temp]')
        print('remove    : remove a preset')
        print('       syntax : remove [preset]')
        print('edit      : edit a value')
        print('       syntax : edit [preset] [key] [new value]')
        print('       keys   :')
        print('                name    : preset name')
        print('                tdpr    : tdp ratio')
        print('                tmpr    : temp ratio')
        print('                max_tdp : maximum tdp')
        print('                max_tmp : maximum temp')
        print('                min_tdp : minimum tdp')
        print('                min_tmp : minimum temp')
        print('ryzenadj   : return the output of ryzenadj -i')
    elif command[1] == 'mode':
        conn.send(command[1] + ' ' + command[2])
        print(conn.recv())
    elif command[1] == 'ratio':
        conn.send(command[1] + ' ' + command[2] + ' ' + command[3])
        print(conn.recv())
    elif command[1] == 'manual':
        if command[1] == 'tdp' or command[1] == 'temp':
            conn.send(command[1] + ' ' + command[2] + ' ' + command[3])
            print(conn.recv())
    elif command[1] == 'list_proc':
        proc = os.popen('ps h -eo command').read().rstrip().split('\n')
        try:
            arg = command[2]
            for i in range(len(proc)):
                if arg in proc[i]:
                    print(proc[i])

        except:
            print(proc)
    elif command[1] == 'add_mode':
        conn.send(command[1])

        if conn.recv() == 'ready':
            conn.send(command[2])
            print('sent mode name')

        if conn.recv() == 'ready1':
            conn.send(command[3])
            print('sent tdp ratio')

        if conn.recv() == 'ready2':
            conn.send(command[4])
            print('sent temp ratio')

        if conn.recv() == 'ready3':
            conn.send(command[5])
            print('sent max tdp')

        if conn.recv() == 'ready4':
            conn.send(command[6])
            print('sent max temp')

        if conn.recv() == 'ready5':
            conn.send(command[7])
            print('sent min tdp')

        if conn.recv() == 'ready6':
            conn.send(command[8])
            print('sent min temp')

        print('command send')
        print(conn.recv())

    elif command[1]== 'state':
        conn.send(command[1])
        print(conn.recv())
    elif command[1] == 'remove':
        conn.send(command[1] + ' ' + command[2])
        print(conn.recv())
    elif command[1] == 'edit':
        conn.send(command[1] + ' ' + command[2] + ' ' + command[3] + ' ' + command[4])
        print(conn.recv())
    elif command[1] == 'ryzenadj':
        conn.send(command[1])
        print(conn.recv())
    elif command[1] == 'change_key':
        conn.send(command[1] + ' ' + command[2])
        storage['connection']['authkey'] = command[2]
        writecfg(storage)
        print(conn.recv())
else:
    pass

conn.close()
