import os
import visa
import time
from config import Config
from prettytable import PrettyTable


class Instrument:
    def __init__(self, mainProg):
        self.parent = mainProg
        self.config = Config(mainProg)

        self.span = self.parent.limitsAmpl.get('freqstop') - self.parent.limitsAmpl.get('freqstart')
        self.center = self.parent.limitsAmpl.get('freqstart') + self.span / 2

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
        self.sa.write(":DISP:WIND:TRAC:Y:DLIN {} dBm".format(line))
        self.sa.write(":DISP:WIND:TRAC:Y:DLIN:STAT 1")
        self.sa.write(":BAND:VID:AUTO 27 KHz")
        # self.sa.write(":BAND:VID:AUTO ON")
        # self.sa.write(":BAND:RES:AUTO ON")
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

    def setGenPow(self, need):
        self.sa.write(":SENSE:FREQ:center {} MHz".format(self.center))
        self.sa.write("DISP:WIND:TRAC:Y:RLEV:OFFS {}".format(self.getOffset()))
        self.sa.write(":POW:ATT 0")
        self.sa.write(":DISP:WIND:TRAC:Y:RLEV {}".format(float(self.getOffset()) - 10))
        genList = (self.gen1, self.gen2)
        for curGen, freq in enumerate([self.center - 0.3, self.center + 0.3]):
            self.sa.write(":CALC:MARK1:STAT ON")
            self.sa.write(":CALC:MARK1:X {} MHz".format(freq))
            gen = genList[curGen]
            gen.write(":FREQ:FIX {} MHz".format(freq))
            gen.write("POW:AMPL -65 dBm")
            gen.write(":OUTP:STAT ON")
            time.sleep(1)
            self.setGainTo(gen=gen, need=need)
            gen.write(":OUTP:STAT OFF")
        self.gen1.write(":OUTP:STAT ON")
        self.gen2.write(":OUTP:STAT ON")
        time.sleep(1)

    def setGainTo(self, gen, need):
        gain = float(self.sa.query("CALC:MARK1:Y?"))
        genPow = float(gen.query("POW:AMPL?"))
        acc = 0.05
        while not (gain - acc <= need <= gain + acc):
            if genPow >= 0:
                gen.write("POW:AMPL -65 dBm")
                self.gen1.write(":OUTP:STAT OFF")
                self.gen2.write(":OUTP:STAT OFF")
                raw_input("Gain problem. Press enter for continue...")
                self.parent.mainMenu()
            gen.write("POW:AMPL {} dBm".format(genPow))
            gain = float(self.sa.query("CALC:MARK1:Y?"))
            time.sleep(.1)
            delta = abs(need - gain)
            if delta <= 5:
                steep = delta
            # elif delta <= 5:
            #     steep = 0.5
            elif delta <= 10:
                steep = 1
            else:
                steep = 5
            if gain < need:
                genPow += steep
            else:
                genPow -= steep

    def getOffset(self):
        try:
            offList = []
            f = open(self.config.getConfAttr('settings', 'calibrationFile'), "r")
            for line in f:
                off = line.strip().split(';')
                off[0] = float(off[0])/1000000
                offList.append(off)
            for n in offList:
                if n[0] <= self.center < n[0] + 70:
                    return n[1]
        except Exception as e:
            print(str(e))
            raw_input('Calibration data file open error. Press enter for continue...')
            self.parent.mainMenu()
