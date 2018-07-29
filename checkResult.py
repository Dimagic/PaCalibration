import os
import time
from progressbar import ProgressBar
from config import Config
from prettytable import PrettyTable
from loopTwo import LoopTwo


class FullBandResult:
    def __init__(self, mainProg):
        self.parent = mainProg
        self.config = Config(mainProg)
        self.instrument = self.parent.instrument

        self.span = self.parent.limitsAmpl.get('freqstop') - self.parent.limitsAmpl.get('freqstart')
        self.center = self.parent.limitsAmpl.get('freqstart') + self.span / 2
        self.harmonyLimit = self.parent.limitsAmpl.get('l2_limit')
        self.needSaGain = self.parent.limitsAmpl.get('needGain')

        self.sa = self.instrument.saPreset(freq=self.center, line=self.harmonyLimit)
        self.gen1, self.gen2 = self.instrument.genPreset(freq=self.center)
        self.checkResult()

    def checkResult(self):
        tableResult = PrettyTable(["N", "Freq", "Power", "Density"])
        nn = 0
        freqDict = {}
        freq = self.parent.limitsAmpl.get('freqstart')
        pbar = ProgressBar(maxval=self.span)
        pbar.start()
        self.instrument.setGenPow(need=self.needSaGain)
        # self.sa.write(":CONF:CHP")
        self.sa.write(":CALC:MARK1:STAT ON")
        self.sa.write(":CALC:MARK2:STAT ON")
        while freq <= self.parent.limitsAmpl.get('freqstop'):
            nn += 1
            self.sa.write(":SENSE:FREQ:center {} MHz".format(freq))
            self.gen1.write(":FREQ:FIX {} MHz".format(freq - 0.3))
            self.gen2.write(":FREQ:FIX {} MHz".format(freq + 0.3))
            self.sa.write(":CALC:MARK1:X {} MHz".format(freq - 0.9))
            self.sa.write(":CALC:MARK2:X {} MHz".format(freq + 0.9))
            # pow = round(float(self.sa.query(":MEAS:CHP:CHP?")), 2)
            time.sleep(.5)
            pow = 1
            m1 = round(float(self.sa.query("CALC:MARK1:Y?")), 2)
            m2 = round(float(self.sa.query("CALC:MARK2:Y?")), 2)
            den = max(m1, m2)
            # gainList = self.getGainList()
            tableResult.add_row([nn, freq, pow, den])
            freqDict.update({nn: float(freq)})
            freq += 5
            pbar.update(nn)
        self.sa.write("INIT:CONT ON")
        pbar.finish()
        self.gen1.write(":OUTP:STAT OFF")
        self.gen2.write(":OUTP:STAT OFF")
        print(tableResult)
        while True:
            print("1: Set freq for manual calibration")
            print("2: Set freq for Loop2 calibration")
            print("0: Continue")
            try:
                k = int(input("Choose operation: "))
            except:
                continue
            if k == 1:
                n = input("Choose number of freq: ")
                try:
                    freq = freqDict.get(n)
                except:
                    raw_input("Incorrect number of freq. Press enter for continue...")
                    os.system("cls")
                    print(tableResult)
                    continue
                self.sa.write(":SENSE:FREQ:center {} MHz".format(freq))
                self.gen1.write(":FREQ:FIX {} MHz".format(freq - 0.3))
                self.gen2.write(":FREQ:FIX {} MHz".format(freq + 0.3))
                self.gen1.write(":OUTP:STAT ON")
                self.gen2.write(":OUTP:STAT ON")
                raw_input("Press enter for continue")
                self.gen1.write(":OUTP:STAT OFF")
                self.gen2.write(":OUTP:STAT OFF")
                os.system("cls")
                self.checkResult()
            elif k == 2:
                pass
                if k in freqDict.keys():
                    LoopTwo(self.parent, None)
                    os.system("cls")
                    self.checkResult()
            elif k == 0:
                return
            else:
                os.system("cls")
                print(tableResult)

    def setMarkers(self, freq):
        self.markFreqList = (freq - .9, freq + .9)
        for i, freq in enumerate(self.markFreqList):
            i += 1
            self.sa.write(":CALC:MARK{}:STAT ON".format(i))
            self.sa.write(":CALC:MARK{}:X {} MHz".format(i, self.markFreqList[i - 1]))

    def getGainList(self):
        gainList = []
        for i in xrange(len(self.markFreqList)):
            gain = self.sa.query("CALC:MARK{}:Y?".format(i + 1))
            gainList.append(round(float(gain), 2))
        return gainList

    def getMaxHarmony(self):
        return max(self.getGainList())
