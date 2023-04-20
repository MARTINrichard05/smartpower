#!/usr/bin/python
import time
from time import monotonic

from multiprocessing.connection import Client, Listener

from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Static, DataTable, Label, TextLog, Input
from textual.widget import Widget
from textual.reactive import reactive

import json
import subprocess
import os
from time import sleep

#class Simpledisplay(Static):
#    """A widget to display elapsed time."""


class (Static):
    def on_mount(self) -> None:
        self.text_log = self.query_one(TextLog)

    def on_button_pressed(self, event: Button.Pressed):
        button_id = event.button.id
        if button_id == "refresh_button":
            self.reload()
    def reload(self):
        conn.send('ryzenadj')
        infos = str(conn.recv())
        infos = infos.split('\n')
        self.text_log.write(infos[6])
        self.text_log.write(infos[7])
        self.text_log.write(infos[24])
        self.text_log.write(infos[25])
    def compose(self) -> ComposeResult:
        yield Container(TextLog(classes='infotext'),Button('refresh', id='refresh_button'), classes='info')

class Datatables(Static):

    def on_mount(self) -> None:
        self.selected_mode = []
        self.values = ['name', 'tdpr', 'tmpr', 'max_tdp', 'max_tmp', 'min_tdp', 'min_tmp']
        self.table = self.query_one(DataTable)
        self.text_log = self.query_one(TextLog)
        first_row = [
            ('mode name', 'tdp ratio', 'temp ratio', 'maximum tdp', 'maximum temp', 'minimum tdp', 'minimum temp')]
        row = iter(first_row)
        self.table.add_columns(*next(row))
        self.reload()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        if button_id == "refresh_button":
            self.reload()
        elif button_id == "send_button":
            conn.send('mode ' +self.selected_mode[0])
            self.text_log.write('send to daemon >>> mode ' + self.selected_mode[0])
            self.text_log.write('daemon responded >>> ' + str(conn.recv()))
            self.reload()
        elif button_id == 'help_codes_button':
            self.text_log.write('--------------------------------')
            self.text_log.write('200 : ok')
            self.text_log.write('404 : not found (try to refresh)')
            self.text_log.write('--------------------------------')
        elif button_id == 'clear_button':
            self.text_log.clear()
        elif button_id == 'new_preset_button':
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

            self.text_log.write('created new default preset')
            self.text_log.write('daemon responded >>> ' + str(conn.recv()))
            self.reload()
        elif button_id == 'delete_preset_button':
            conn.send('delete '+ self.selected_mode[0])
            self.text_log.write('send to daemon >>> delete ' + self.selected_mode[0])
            self.text_log.write('daemon responded >>> ' + str(conn.recv()))
            self.reload()


    def reload(self) -> None:

        conn.send('state')
        data = conn.recv()
        # data = json.load(json_data)
        self.modelist = []
        for i in range(len(list(data["modes"]))):
            currentmode = list(data["modes"])[i]
            self.modelist.append((str(currentmode), data['modes'][currentmode]['tdpr'], data['modes'][currentmode]['tmpr'],
                             data['modes'][currentmode]['max_tdp'], data['modes'][currentmode]['max_tmp'],
                             data['modes'][currentmode]['min_tdp'], data['modes'][currentmode]['min_tmp']))


        rows = iter(self.modelist)
        self.table.clear()
        self.table.add_rows(rows)

    def action_refresh(self) -> None:
        self.reload()
    def on_data_table_cell_selected(self, event: DataTable.CellSelected) :
        event.stop()
        self.selected_mode = self.modelist[event.coordinate.row]
        self.selected_value = self.values[event.coordinate.column]
        self.text_log.write('selected mode : '+ self.selected_mode[0])


    def on_input_submitted(self, event: Input.Submitted):
        event.stop()
        conn.send('edit '+str(self.selected_mode[0]) + ' ' + self.selected_value + ' '+ event.value)
        self.text_log.write('send to daemon >>> edit ' + str(self.selected_mode[0]) + ' ' + self.selected_value + ' '+ event.value)
        self.text_log.write('daemon responded >>> ' + str(conn.recv()))
        self.reload()


    def compose(self) -> ComposeResult:
        #yield Container(, classes= 'buttons')
        yield DataTable(classes= 'datatable')
        yield Container(TextLog(), classes= 'log')
        yield Container(Input(placeholder="enter new value", classes='margin'),Container( Button('new preset', id='new_preset_button', classes='margin', variant="success"), Button('delete', id='delete_preset_button', classes='margin', variant="error"), Button("codes help", id='help_codes_button', classes='margin', variant="primary"), Button("clear", id='clear_button', classes='margin', variant="error"), Button("refresh", id='refresh_button', variant="primary", classes='margin'), Button("set current", id='send_button', variant="success", classes='margin'), classes='edit3'), classes='edit2')
        #yield Container(Button('new preset', id='new_preset_button', classes='blue'), Button('delete', id='delete_preset_button', classes='red'), classes='edit')


class SmartPowerCtrlTui(App):
    CSS_PATH = "SmartPowerCtrlTuiCss.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),("r", "refresh", "Resfresh mode list and info") ,("t", "jsmonreuf", "Resfresh mode list and info")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Container(Datatables(), Infos())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark





if __name__ == "__main__":

    user = subprocess.check_output(['whoami'], shell=True, text=True).split('\n')[0]
    path = '/home/' + user + '/.config/SmartRyzenManager/'
    storage = {}


    def readcfg():
        with open(path + 'storage-ctrl.json') as json_file:
            return json.load(json_file)


    def writecfg():
        with open(path + 'storage-ctrl.json', 'w') as fp:
            json.dump(storage, fp)


    try:
        storage = readcfg()
    except:
        storage = {'connection': {'adress': 'localhost', 'port': 6000, 'authkey': 'eogn68rb8r69'}, }
        os.system('mkdir ~/.config/SmartRyzenManager')
        writecfg()

    conn = Client((storage['connection']['adress'], storage['connection']['port']),
                  authkey=bytes(storage['connection']['authkey'], 'ascii'))

    app = SmartPowerCtrlTui()
    app.run()
