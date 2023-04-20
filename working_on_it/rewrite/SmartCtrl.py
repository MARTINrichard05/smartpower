#!/usr/bin/python
import time
from time import monotonic

from multiprocessing.connection import Client, Listener

from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Static, DataTable, Label, TextLog, Input
from textual.widget import Widget
from textual.reactive import reactive
from textual.screen import Screen

import json
import subprocess
import os
from time import sleep

class infos(Static):
    def compose(self):
        yield TableModes()
class UserInput(Static):
     def compose(self):
         yield Buttons()
class TableModes(Static):
    def on_mount(self) -> None:
        self.values = ['name', 'tdpr', 'tmpr', 'max_tdp', 'max_tmp', 'min_tdp', 'min_tmp']
        self.table = self.query_one(DataTable)
        #self.text_log = self.query_one(TextLog)
        first_row = [
            ('mode name', 'tdp ratio', 'temp ratio', 'maximum tdp', 'maximum temp', 'minimum tdp', 'minimum temp')]
        row = iter(first_row)
        self.table.add_columns(*next(row))
        self.set_interval(1, self.reload)
    def reload(self) -> None:
        global events
        if len(events) >0:
            for i in events:
                if i[0] == 'input':
                    events.remove(i)
                    conn.send

        global daemon_state
        conn.send('state')
        daemon_state = conn.recv()
        # data = json.load(json_data)
        self.modelist = []
        for i in range(len(list(daemon_state["modes"]))):
            currentmode = list(daemon_state["modes"])[i]
            self.modelist.append(
                (str(currentmode), daemon_state['modes'][currentmode]['tdpr'], daemon_state['modes'][currentmode]['tmpr'],
                 daemon_state['modes'][currentmode]['max_tdp'], daemon_state['modes'][currentmode]['max_tmp'],
                 daemon_state['modes'][currentmode]['min_tdp'], daemon_state['modes'][currentmode]['min_tmp']))

        rows = iter(self.modelist)
        self.table.clear()
        self.table.add_rows(rows)
        self.table.cursor_coordinate = (list(daemon_state["modes"]).index(daemon_state['data']['etc']['mode']), 0)
        self.selected_mode = self.modelist[list(daemon_state["modes"]).index(daemon_state['data']['etc']['mode'])]

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) :
        event.stop()
        self.selected_mode = self.modelist[event.coordinate.row]
        self.selected_value = self.values[event.coordinate.column]
        conn.send('mode ' +self.selected_mode[0])
        conn.recv()
        #self.reload()
    def compose(self) -> ComposeResult:
        #yield Container(, classes= 'buttons')
        yield DataTable(classes= 'MData')

class edit_box(Static):
    def compose(self):
        yield Input(placeholder='press enter to apply')
    def on_input_submitted(self, event: Input.Submitted):
        event.stop()
        global events
        events.append(('input', event.value))

class Buttons(Static):

    def on_button_pressed(self, event: Button.Pressed):
        button_id = event.button.id
        if button_id == "new_preset":
            conn.send('add_mode')
            if conn.recv() == 'ready':
                conn.send('new')

            if conn.recv() == 'ready1':
                conn.send(1)

            if conn.recv() == 'ready2':
                conn.send(1)

            if conn.recv() == 'ready3':
                conn.send(25000)

            if conn.recv() == 'ready4':
                conn.send(80)

            if conn.recv() == 'ready5':
                conn.send(6500)

            if conn.recv() == 'ready6':
                conn.send(65)
            conn.recv()
    def compose(self) -> None:
        yield (Button('send', id='new_preset'))

class Main(App):
    CSS_PATH = "SmartCtrl.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("r", "refresh", "Resfresh mode list and info"),
                ("t", "toggle_screen", "Resfresh mode list and info")]
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Container(infos(),UserInput() , classes='main_container')


    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

if __name__ == "__main__":
    print('starting')

    user = subprocess.check_output(['whoami'], shell=True, text=True).split('\n')[0]
    path = '/home/' + user + '/.config/SmartRyzenManager/'
    #storage = {}


    def readcfg():
        with open(path + 'storage-ctrl.json') as json_file:
            return json.load(json_file)


    def writecfg(storage):
        with open(path + 'storage-ctrl.json', 'w') as fp:
            json.dump(storage, fp)


    try:
        storage = readcfg()
    except:
        storage = {'connection': {'adress': 'localhost', 'port': 6000, 'authkey': 'eogn68rb8r69'}, }
        os.system('mkdir ~/.config/SmartRyzenManager')
        writecfg(storage)

    conn = Client((storage['connection']['adress'], storage['connection']['port']),
                  authkey=bytes(storage['connection']['authkey'], 'ascii'))
    daemon_state = {}
    events = []
    toggle = False

    app = Main()
    app.run()