import re
import sys
import os
from biasCalibrate import BiasCalibrate
from config import Config
from test5 import Test5
from instrument import Instrument
import serial.tools.list_ports

__version__ = '0.0.4'


class Main:
    def __init__(self):
        self.config = Config(self)
        self.limitsAmpl = {}
        self.mainMenu()

    def mainMenu(self):
        os.system("cls")
        print(__version__)
        print("********************************")
        print("******** PA Calibration ********")
        print("********************************")
        print("1: Calibrate")
        print("8: Set instruments")
        print("9: Set COM port")
        print("0: Exit")
        print("********************************")
        print("Current port: {}".format(self.config.getConfAttr('settings', 'comPort')))
        print("********************************")

        try:
            menu = int(input("Choose operation: "))
        except Exception:
            self.mainMenu()
        if menu == 1:
            if self.config.getConfAttr('settings', 'comPort') == "None":
                try:
                    raw_input("Port not selected. Press enter for choose...")
                    self.setComPort()
                except SyntaxError:
                    pass
            else:
                port = self.config.getConfAttr('settings', 'comPort')
                portList = []
                for n in list(serial.tools.list_ports.comports()):
                    portList.append(re.search('COM[0-9]{1,3}', str(n)).group(0))
                if port not in portList:
                    try:
                        raw_input("{} not available in system. Press enter for choose port...".format(port))
                        self.setComPort()
                    except SyntaxError as e:
                        print(str(e))
            self.checkInstruments()
            self.limitsAmpl = {}
            self.getLimits()
            Wnd_Main = Test5(self)
            Wnd_Main.test5Connection(1)
            Wnd_Node = Wnd_Main.connectAddNode()
            BiasCalibrate(Wnd_Main.Wnd_NodeEdit)
        if menu == 8:
            instr = Instrument(self)
            instr.menu()
            instr.getListInstrument()
        if menu == 9:
            self.setComPort()
        elif menu == 0:
            sys.exit(0)
        else:
            self.mainMenu()

    def setComPort(self):
        listPorts = list(serial.tools.list_ports.comports())
        if len(listPorts) == 0:
            self.config.setConfAttr('settings', 'comPort', 'None')
            try:
                raw_input("Available ports not found. Press enter for continue...")
                self.mainMenu()
            except SyntaxError:
                pass
        os.system("cls")
        print("COM port selection")
        tmp = {}
        for i, j in enumerate(listPorts):
            tmp.update({i: re.search('COM[0-9]{1,3}', str(j)).group(0)})
            print("{}: {}".format(i, j))
        try:
            nport = int(input("Choose COM port: "))
        except Exception:
            self.setComPort()
        if nport not in tmp.keys():
            self.setComPort()
        self.config.setConfAttr('settings', 'comPort', str(tmp.get(nport)))
        self.mainMenu()

    def checkInstruments(self):
        # TODO: available instruments
        currInstr = dict(self.config.config.items('instruments'))
        if 'None' in currInstr.values():
            raw_input('Not all the necessary instruments are selected or available. Press enter for continue...')
            self.mainMenu()

    def getLimits(self):
        os.system("cls")
        barcode = raw_input('Scan barcode: ')
        res = re.findall(r'[a-zA-Z0-9]+', barcode)
        if len(res) != 2:
            raw_input('Incorrect barcode. Press enter for continue...')
            self.mainMenu()
        if len(res[1]) != 4 or len(re.findall(r'[0-9]', res[1])) != 0:
            raw_input('Incorrect serial number. Press enter for continue...')
            self.mainMenu()
        key = self.config.getConfAttr('limits', 'keys').split(';')
        val = self.config.getConfAttr('limits', res[0]).split(';')
        if len(key) != len(val):
            raw_input('Incorrect limits length. Check config file...')
            self.mainMenu()
        for i, j in enumerate(key):
            try:
                self.limitsAmpl.update({j: float(val[i])})
            except Exception as e:
                print(str(e))
                raw_input('Incorrect limits data. Check config file...')
                self.mainMenu()


if __name__ == '__main__':
    prog = Main()
    sys.exit(0)