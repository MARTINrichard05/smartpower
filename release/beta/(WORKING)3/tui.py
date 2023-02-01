#!/usr/bin/python
from multiprocessing.connection import Client
import os
from sys import stdin, stdout

address = ('localhost', 6000)
#conn = Client(address, authkey=b'eogn68rb8r69')
# can also send arbitrary objects:
# conn.send(['a', 2.5, None, int, sum])
#conn.close()
class Main:
    def __init__(self):
        self.conn = Client(address, authkey=b'eogn68rb8r69')
        self.main()
    def send(self, data):
        try:
            self.conn.send(data)
        except :
            pass
    def main(self):
        while True:
            command1 = stdin.readline()
            command = command1.split(' ')
            if command[0] == 'help':
                print('A way to interact without root privileges with my smartpower daemon')
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
            elif command[0] == 'mode':
                self.send(command[0] + ' ' + command[1])
            elif command[0] == 'ratio':
                self.send(command[0] + ' ' + command[1] + ' ' + command[2])
            elif command[0] == 'manual':
                if command[1] == 'tdp' or command[1] == 'temp':
                    self.send(command[0] + ' ' + command[1] + ' ' + command[2])
            elif command[0] == 'list_proc':
                proc = os.popen('ps h -eo command').read().rstrip().split('\n')
                try :
                    arg = command[1]
                    for i in range(len(proc)):
                        if arg in proc[i]:
                            print(proc[i])

                except:
                    print(proc)
            elif command[0] == 'add_proc':
                self.send(command[0] + ' ' + command[1] + ' '+ command[2]+ ' ' + command[3])
            elif command[0] == 'exit':
                self.conn.close()
                break






if __name__ == '__main__':
    a = Main()

