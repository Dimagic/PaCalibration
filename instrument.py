import os
import visa
from config import Config


class Instrument:
    def __init__(self, mainProg):
        self.parent = mainProg
        self.config = Config(mainProg)
        self.config.getConfAttr('instruments', 'na')
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
        print("********************************")
        print("Available instruments:")
        print("********************************")
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
        except Exception:
            self.menuSetInstrumentType()
        if instrType not in forSelect.keys():
            self.menuSetInstrumentType()
        else:
            listInstr = self.rm.list_resources()
            if len(listInstr) == 0:
                print('Available instruments not found. Press enter for return to main menu...')
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
                self.config.setConfAttr('instruments', forSelect.get(instrType), 'None')
            else:
                self.config.setConfAttr('instruments', forSelect.get(instrType), dictInstr.get(instrModel))
            self.menu()

    def fillMenuCurrInstr(self):
        currInstr = dict(self.config.config.items('instruments'))
        listNameRes = self.getListInstrument()
        for i in currInstr.keys():
            if currInstr.get(i).decode('utf-8') == 'None':
                print('{} : {}'.format(i.decode('utf-8').upper(), currInstr.get(i).decode('utf-8')))
                continue
            if currInstr.get(i).decode('utf-8') in listNameRes:
                status = 'Availabe'
            else:
                status = 'Not availabe'
            print('{} : {} : {}'.format(i.decode('utf-8').upper(), currInstr.get(i).decode('utf-8'), status))

    def getListInstrument(self):
        listRes = self.rm.list_resources()
        listNameRes = []
        for i in listRes:
            instr = self.rm.open_resource(i, send_end=False)
            listNameRes.append(instr.query('*IDN?').split(',')[1])
        return listNameRes

    def getInstr(self, val):
        listRes = self.rm.list_resources()
        for i in listRes:
            instr = self.rm.open_resource(i, send_end=False)
            if val.upper() == instr.query('*IDN?').split(',')[1].upper():
                return instr
        return None

    def multiInit(self):
        # TODO: multimeter initialisation
        pass

    def multiGetData(self):
        # TODO: multimeter get data
        pass

