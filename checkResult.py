from config import Config
from instrument import Instrument
import time


class FullBandResult:
    def __init__(self, mainProg):
        self.parent = mainProg
        self.config = Config(mainProg)
        self.instrument = self.parent.instrument

        self.span = self.parent.limitsAmpl.get('freqstop') - self.parent.limitsAmpl.get('freqstart')
        self.center = self.parent.limitsAmpl.get('freqstart') + self.span / 2

        self.harmonyLimit = -30

        self.sa = self.instrument.saPreset(freq=self.center, line=self.harmonyLimit)
        self.gen1, self.gen2 = self.instrument.genPreset(freq=self.center)
        self.checkResult()

    def checkResult(self):
        freq = self.parent.limitsAmpl.get('freqstart') + 1
        self.setGenPow(need=30)
        while freq <= self.parent.limitsAmpl.get('freqstop') - 1:
            self.setMarkers(freq - 1)
            self.sa.write(":SENSE:FREQ:center {} MHz".format(freq))
            self.gen1.write(":FREQ:FIX {} MHz".format(freq - 0.3))
            self.gen2.write(":FREQ:FIX {} MHz".format(freq + 0.3))
            time.sleep(.5)
            print("Freq: {} Avg Gain: {}".format(freq, self.getMaxHarmony()))
            freq += 1
        self.gen1.write(":OUTP:STAT OFF")
        self.gen2.write(":OUTP:STAT OFF")

    def setGenPow(self, need):
        self.sa.write("DISP:WIND:TRAC:Y:RLEV:OFFS {}".format(self.getOffset()))
        genList = (self.gen1, self.gen2)
        for curGen, freq in enumerate([self.center - 0.3, self.center + 0.3]):
            self.sa.write(":CALC:MARK1:STAT ON")
            self.sa.write(":CALC:MARK1:X {} MHz".format(freq))
            gen = genList[curGen]
            gen.write(":FREQ:FIX {} MHz".format(freq))
            gen.write("POW:AMPL -20 dBm")
            gen.write(":OUTP:STAT ON")
            time.sleep(1)
            self.setGainTo(gen, need)
            gen.write(":OUTP:STAT OFF")
        self.gen1.write(":OUTP:STAT ON")
        self.gen2.write(":OUTP:STAT ON")

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

    def setMarkers(self, freq):
        self.markFreqList = (freq - .9, freq + .9)
        for i, freq in enumerate(self.markFreqList):
            i += 1
            self.sa.write(":CALC:MARK{}:STAT ON".format(i))
            self.sa.write(":CALC:MARK{}:X {} MHz".format(i, self.markFreqList[i - 1]))

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

    def getGainList(self):
        gainList = []
        for i in xrange(len(self.markFreqList)):
            gain = self.sa.query("CALC:MARK{}:Y?".format(i + 1))
            gainList.append(round(float(gain), 2))
        return gainList

    def getMaxHarmony(self):
        return max(self.getGainList())

    def setGainTo(self, gen, need):
        gain = float(self.sa.query("CALC:MARK1:Y?"))
        genPow = float(gen.query("POW:AMPL?"))
        acc = 0.03
        while not (gain - acc <= need <= gain + acc):
            if genPow >= 0:
                gen.write(":OUTP:STAT OFF")
                raw_input("Gain problem. Press enter for continue...")
                self.parent.mainMenu()
            gen.write("POW:AMPL {} dBm".format(genPow))
            gain = float(self.sa.query("CALC:MARK1:Y?"))
            time.sleep(.1)
            delta = need - gain
            if delta <= 0.5:
                steep = 0.01
            elif delta <= 2:
                steep = 0.5
            else:
                steep = 1
            if gain < need:
                genPow += steep
            else:
                genPow -= steep