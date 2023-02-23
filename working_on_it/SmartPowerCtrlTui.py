from time import monotonic

from multiprocessing.connection import Client, Listener

from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Static, DataTable, Label
from textual.widget import Widget
from textual.reactive import reactive

import json
import subprocess
import os

class Simpledisplay(Static):
    """A widget to display elapsed time."""



class Datatables(Static):


    def on_mount(self) -> None:
        self.selected_mode = []
        self.table = self.query_one(DataTable)
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
            self.table.add_rows([[str(self.selected_mode[0])]])
            self.table.add_rows([[str(conn.recv())]])

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
    def on_data_table_cell_selected(
        self, event: DataTable.CellSelected
    ) :
        event.stop()
        self.selected_mode = self.modelist[event.coordinate.row]

    def compose(self) -> ComposeResult:
        #yield Container(, classes= 'buttons')
        yield Container(DataTable(), Container( Button("refresh", id='refresh_button'), Button("send", id='send_button'), classes='buttons'), classes= 'datatable')


class SmartPowerCtrlTui(App):
    CSS_PATH = "SmartPowerCtrlTuiCss.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),("r", "refresh", "Resfresh mode list and info") ,("t", "jsmonreuf", "Resfresh mode list and info")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Container(Datatables())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark





if __name__ == "__main__":

    user = subprocess.check_output(['whoami'], shell=True, text=True).split('\n')[0]
    path = '/home/' + user + '/.config/smartpower/'
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
        os.system('mkdir ~/.config/smartpower')
        writecfg()

    conn = Client((storage['connection']['adress'], storage['connection']['port']),
                  authkey=bytes(storage['connection']['authkey'], 'ascii'))

    app = SmartPowerCtrlTui()
    app.run()
