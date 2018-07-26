import os
import visa
from config import Config
from prettytable import PrettyTable


class Instrument:
    def __init__(self, mainProg):
        self.parent = mainProg
        self.config = Config(mainProg)
        self.sa = None
        self.gen1 = None
        self.gen2 = None
        try:
            self.rm = visa.ResourceManager()
            self.rm.timeout = 50000
        except Exception as e:
            print('Error: {}'.format(str(e)))
            raw_input('Press enter for return continue...')
            mainProg.mainMenu()
        # self.menu()

    def menu(self):
        os.system("cls")
        print("********************************")
        print("Current instruments:")
        print("********************************")
        self.fillMenuCurrInstr()
        print("1: Set instrument")
        print("0: Back")

        try:
            menu = int(input("Choose operation: "))
        except Exception:
            self.parent.mainMenu()
        if menu == 1:
            self.menuSetInstrumentType()
        if menu == 0:
            self.parent.mainMenu()
        else:
            self.menu()

    def menuSetInstrumentType(self):
        currInstr = dict(self.config.config.items('instruments')).keys()
        forSelect = {}
        os.system("cls")
        for i, j in enumerate(currInstr):
            j = j.upper()
            forSelect.update({i: j.decode('utf-8')})
            print('{}: {}'.format(i, j))
        try:
            instrType = int(raw_input('Choose instrument type: '))
        except Exception as e:
            raw_input(str(e))
            self.menuSetInstrumentType()
        if instrType not in forSelect.keys():
            self.menuSetInstrumentType()
        else:
            listInstr = self.rm.list_resources()
            if len(listInstr) == 0:
                raw_input('Available instruments not found. Press enter for return to main menu...')
                self.parent.mainMenu()
            dictInstr = {}
            for i, j in enumerate(listInstr):
                instr = self.rm.open_resource(j, send_end=False)
                dictInstr.update({i: instr.query('*IDN?').split(',')[1]})
                print('{}: {}'.format(i, instr.query('*IDN?')))
            print('{}: {}'.format(10, 'None'))
            try:
                instrModel = int(raw_input('Choose instrument: '))
            except Exception:
                self.menuSetInstrumentType()
            if instrModel == 10:
                self.config.setConfAttr('instruments', forSelect.get(instrType), '')
            else:
                self.config.setConfAttr('instruments', forSelect.get(instrType), dictInstr.get(instrModel))
            self.menu()

    def fillMenuCurrInstr(self):
        currInstr = dict(self.config.config.items('instruments'))
        listNameRes = self.getListInstrument()
        tableInstr = PrettyTable(["Type", "Model", "Availability"])
        for i in currInstr.keys():
            if currInstr.get(i).decode('utf-8') in ('None', ''):
                # print('{} : {}'.format(i.decode('utf-8').upper(), currInstr.get(i).decode('utf-8')))
                tableInstr.add_row([i.decode('utf-8').upper(), currInstr.get(i).decode('utf-8'), ''])
                continue
            if currInstr.get(i).decode('utf-8') in listNameRes:
                status = 'Availabe'
            else:
                status = 'Not availabe'
            tableInstr.add_row([i.decode('utf-8').upper(), currInstr.get(i).decode('utf-8'), status])
        print(tableInstr)

    def getListInstrument(self):
        listRes = self.rm.list_resources()
        listNameRes = []
        for i in listRes:
            instr = self.rm.open_resource(i, send_end=False)
            listNameRes.append(instr.query('*IDN?').split(',')[1].replace(' ', ''))
        return listNameRes

    def getInstr(self, val):
        listRes = self.rm.list_resources()
        for i in listRes:
            instr = self.rm.open_resource(i, send_end=False)
            currInstr = instr.query('*IDN?').split(',')[1].upper().replace(' ', '')
            if val.upper() == currInstr.upper():
                return instr
        return None

    def saPreset(self, freq, line):
        self.sa = self.getInstr(self.config.getConfAttr('instruments', 'sa'))
        self.sa.write(":SYST:PRES")
        self.sa.write(":CAL:AUTO OFF")
        self.sa.write(":SENSE:FREQ:center {} MHz".format(freq))
        self.sa.write(":SENSE:FREQ:span {} MHz".format(3.5))
        self.sa.write("DISP:WIND:TRAC:Y:DLIN {} dBm".format(line))
        self.sa.write("DISP:WIND:TRAC:Y:DLIN:STAT 1")
        self.sa.write("BAND:VID 27 KHZ")
        return self.sa

    def genPreset(self, freq):
        self.gen1 = self.getInstr(self.config.getConfAttr('instruments', 'gen1'))
        self.gen2 = self.getInstr(self.config.getConfAttr('instruments', 'gen2'))
        self.gen1.write("*RST")
        self.gen1.write(":OUTP:STAT OFF")
        self.gen1.write(":OUTP:MOD:STAT OFF")
        self.gen2.write("*RST")
        self.gen2.write(":OUTP:STAT OFF")
        self.gen2.write(":OUTP:MOD:STAT OFF")

        self.gen1.write(":FREQ:FIX {} MHz".format(freq - 0.3))
        self.gen2.write(":FREQ:FIX {} MHz".format(freq + 0.3))
        return self.gen1, self.gen2
