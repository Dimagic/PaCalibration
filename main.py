import re
import sys
import os
from biasCalibrate import BiasCalibrate
from checkResult import FullBandResult
from config import Config
from loopOne import LoopOne
from loopTwo import LoopTwo
from test5 import Test5
from instrument import Instrument
import serial.tools.list_ports

__version__ = '0.3.3'


class Main:
    def __init__(self):
        self.config = Config(mainProg=self)
        self.instrument = Instrument(mainProg=self)
        self.limitsAmpl = {}
        self.mainMenu()

    def mainMenu(self):
        os.system("cls")
        print(__version__)
        print("********************************")
        print("******** PA Calibration ********")
        print("********************************")
        print("1: Calibrate all")
        print("2: BIAS")
        print("3: LOOP1")
        print("4: LOOP2")
        print("5: Check full band")
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
        if menu in (1, 2, 3, 4, 5):
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
            # TODO: if not all instruments available
            # self.checkInstruments()
            self.limitsAmpl = {}
            self.getLimits()

            if menu in (1, 2, 3, 4):
                Wnd_Main = self.getNode()
            if menu in (1, 2):
                BiasCalibrate(mainProg=self, node=Wnd_Main.Wnd_NodeEdit)
            if menu in (1, 3):
                raw_input('Connect network end press enter...')
                LoopOne(mainProg=self, node=Wnd_Main.Wnd_NodeEdit)
            if menu in (1, 4):
                raw_input('Connect SW1, SW2 end press enter...')
                LoopTwo(mainProg=self, node=Wnd_Main.Wnd_NodeEdit)
            if menu in (1, 5):
                FullBandResult(mainProg=self)
        if menu == 8:
            instr = Instrument(mainProg=self)
            instr.menu()
            instr.getListInstrument()
        if menu == 9:
            self.setComPort()
        elif menu == 0:
            sys.exit(0)
        else:
            self.mainMenu()

    def getNode(self):
        Wnd_Main = Test5(mainProg=self)
        Wnd_Main.test5Connection(1)
        Wnd_Main.connectAddNode()
        return Wnd_Main

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
        if len(res[1]) != 4:
            raw_input('Incorrect serial number. Press enter for continue...')
            self.mainMenu()
        key = self.config.getConfAttr('limits', 'keys').split(';')
        val = self.config.getConfAttr('limits', res[0][:7]).split(';')
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