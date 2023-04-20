#!/usr/bin/python
from multiprocessing.connection import Client
import os
import sys
import time

address = ('localhost', 6000)

conn = Client(address, authkey=b'eogn68rb8r69')

command = sys.argv
if command[1] == 'help':
    print('A way to interact without root privileges with my SmartRyzenManager daemon')
    print(' list of commands available:')
    print('mode : use mode + arg to set it')
    print('       turbo : turn all up to get maximum power (all *ratio , up to the cap)')
    print('       normal : working normally as in config files and the process list')
    print('       eco    : turn tdp down by the wanted ratio but keep temps normals')
    print('       silent : turn down max temp by the wanted ratio to be silent')
    print('       manual : you can can manually set the params')
    print('ratio : set the desired ratio for modes:')
    print('       syntax : [mode] [ratio]')
    print('list_proc : list actives processes , so you can copy the name and use it into the add_proc command')
    print('add_proc : add a process to the list to be used')
    print('       syntax : add_proc [process] [tdp(mW)] [max temp(°C)]')
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
elif command[1] == 'add_proc':
    conn.send(command[1])
    if conn.recv() == 'ready':
        conn.send(command[2])
        print(command)
        print('sendt proc')

    if conn.recv() == 'ready2':
        conn.send(command[3])
        print('sendt tdp')
    if conn.recv() == 'ready3':
        conn.send(command[4])
        print('sendt temp')
    print('command send')
    print(conn.recv())
elif command[1]== 'state':
    conn.send(command[1])
    print(conn.recv())

conn.close()
