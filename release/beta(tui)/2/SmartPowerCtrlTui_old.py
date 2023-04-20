import json
import os
from multiprocessing.connection import Client, Listener
from threading import Thread

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Static, Label
from textual.reactive import reactive
import subprocess
from random import randint


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""
    CSS_PATH = "tui_tests.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        yield Label(connection.test(a))

        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


class connection:
    def __init__(self):
        self.Listener = Listener('localhost', 6001, authkey=bytes(str(key), 'ascii'))
        self.storage = {}
        user = subprocess.check_output(['whoami'], shell=True, text=True).split('\n')[0]
        self.path = '/home/' + user + '/.config/SmartRyzenManager/'

        try:
            self.readcfg()
        except:
            self.storage = {'connection': {'adress': 'localhost', 'port': 6000, 'authkey': 'eogn68rb8r69'}, }
            os.system('mkdir ~/.config/SmartRyzenManager')
            self.writecfg()
        self.connection()

    def connection(self, storage):
        self.conn = Client((storage['connection']['adress'], storage['connection']['port']),
                           authkey=bytes(storage['connection']['authkey'], 'ascii'))

    def listener(self):
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
                                self.storage['modes'][str(name)] = {'tdpr': float(tdpr), 'tmpr': float(tmpr),
                                                                    'max_tdp': int(max_tdp), 'max_tmp': int(max_tmp),
                                                                    'min_tdp': int(min_tdp), 'min_tmp': int(min_tmp), }
                                conn.send(self.storage['modes'])
                                self.writecfg()
                            except Exception as e:
                                conn.send(e)
                        elif tempdata[0] == 'state':
                            conn.send(self.storage)
                        elif tempdata[0] == 'ryzenadj':
                            conn.send(rz.ryzenadj_info())

                self.listener.close()
            except:
                pass

    def readcfg(self):
        with open(self.path + 'storage-ctrl.json') as json_file:
            self.storage = json.load(json_file)

    def writecfg(self):
        with open(self.path + 'storage-ctrl.json', 'w') as fp:
            json.dump(self.storage, fp)


if __name__ == "__main__":
    key = randint(1, 1000000)

    conn_thread = Thread(target=connection)
    conn_thread.start()

    app = StopwatchApp()
    app.run()