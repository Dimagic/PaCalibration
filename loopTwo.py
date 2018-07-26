import time
from config import Config
from instrument import Instrument
from progressbar import ProgressBar


class LoopTwo:
    def __init__(self, mainProg, node):
        self.Wnd_Node = node
        self.parent = mainProg
        self.config = Config(mainProg)

        self.minGain = {}

        self.scrollFase = self.Wnd_Node.TTrackBar2
        self.scrollAmpl = self.Wnd_Node.TTrackBar1
        self.setFaseBtn = self.Wnd_Node.Set2
        self.setAmplBtn = self.Wnd_Node.Set1
        self.getFase = self.Wnd_Node.Edit2
        self.getAmpl = self.Wnd_Node.Edit1

        self.span = self.parent.limitsAmpl.get('freqstop') - self.parent.limitsAmpl.get('freqstart')
        self.center = self.parent.limitsAmpl.get('freqstart') + self.span / 2

        self.harmonyLimit = -30
        self.needSaGain = 30

        self.cw = Instrument(mainProg).getInstr(self.config.getConfAttr('instruments', 'cw'))
        self.sa = Instrument(mainProg).getInstr(self.config.getConfAttr('instruments', 'sa'))
        self.gen1 = Instrument(mainProg).getInstr(self.config.getConfAttr('instruments', 'gen1'))
        self.gen2 = Instrument(mainProg).getInstr(self.config.getConfAttr('instruments', 'gen2'))

        self.cwPreset()
        self.saPreset()
        self.genPreset()

        self.calibration()

    def saPreset(self):
        self.sa.write(":SYST:PRES")
        self.sa.write(":CAL:AUTO OFF")
        self.sa.write(":SENSE:FREQ:center {} MHz".format(self.center))
        self.sa.write(":SENSE:FREQ:span {} MHz".format(3.5))
        self.sa.write("DISP:WIND:TRAC:Y:DLIN {} dBm".format(self.harmonyLimit))
        self.sa.write("DISP:WIND:TRAC:Y:DLIN:STAT 1")
        self.sa.write("BAND:VID 27 KHZ")

    def genPreset(self):
        self.gen1.write("*RST")
        self.gen1.write(":OUTP:STAT OFF")
        self.gen1.write(":OUTP:MOD:STAT OFF")
        self.gen2.write("*RST")
        self.gen2.write(":OUTP:STAT OFF")
        self.gen2.write(":OUTP:MOD:STAT OFF")

        self.gen1.write(":FREQ:FIX {} MHz".format(self.center - 0.3))
        self.gen2.write(":FREQ:FIX {} MHz".format(self.center + 0.3))

    def cwPreset(self):
        pass

    def setMinimum(self):
        self.getFase.set_text(self.minGain.get('FaseData'))
        self.setFaseBtn.Click()
        self.getAmpl.set_text(self.minGain.get('AmplData'))
        self.setAmplBtn.Click()

    def getFirstMinimun(self):
        self.minGain.update({'FaseData': 0, 'AmplData': 0, 'Gain': 1024})
        self.setGenPow(self.needSaGain)
        self.markFreqList = (self.center - .9, self.center + .9)
        for i, freq in enumerate(self.markFreqList):
            i += 1
            self.sa.write(":CALC:MARK{}:STAT ON".format(i))
            self.sa.write(":CALC:MARK{}:X {} MHz".format(i, freq))
        absMin = 0
        absMax =1024
        rSteep = 128
        fBeg = absMin
        fEnd = absMax
        aBeg = absMin
        aEnd = absMax
        pb = 0
        pbar = ProgressBar(maxval=160)
        pbar.start()
        while True:
            rLoopFase = xrange(fBeg, fEnd + rSteep, rSteep)
            rLoopAmpl = xrange(aBeg, aEnd + rSteep, rSteep)
            for i in rLoopFase:
                for j in rLoopAmpl:
                    pb += 1
                    pbar.update(pb)
                    self.getFase.set_text(i)
                    self.setFaseBtn.Click()
                    self.getAmpl.set_text(j)
                    self.setAmplBtn.Click()
                    if self.getAvgGain() < self.minGain.get('Gain'):
                        currGain = self.getAvgGain()
                        self.minGain.update({'FaseData': int(self.getFase.texts()[0]),
                                             'AmplData': int(self.getAmpl.texts()[0]),
                                             'Gain': currGain})
            self.setMinimum()
            rSteep = rSteep / 2
            if rSteep < 1:
                pbar.finish()
                time.sleep(.5)
                return
            fBeg = self.minGain.get('FaseData') - rSteep
            fEnd = self.minGain.get('FaseData') + rSteep

            aBeg = self.minGain.get('AmplData') - rSteep
            aEnd = self.minGain.get('AmplData') + rSteep
            if fBeg < absMin:
                fBeg = absMin
            if fEnd > absMax:
                fEnd = absMax
            if aBeg < absMin:
                aBeg = absMin
            if aEnd > absMax:
                aEnd = absMax

    def setMarkers(self, freq):
        self.markFreqList = (freq - .9, freq + .9)
        for i, freq in enumerate(self.markFreqList):
            i += 1
            self.sa.write(":CALC:MARK{}:STAT ON".format(i))
            self.sa.write(":CALC:MARK{}:X {} MHz".format(i, self.markFreqList[i - 1]))

    def checkResult(self):
        freq = self.parent.limitsAmpl.get('freqstart') + 1
        while freq <= self.parent.limitsAmpl.get('freqstop') - 1:
            self.setMarkers(freq - 1)
            self.sa.write(":SENSE:FREQ:center {} MHz".format(freq))
            self.gen1.write(":FREQ:FIX {} MHz".format(freq - 0.3))
            self.gen2.write(":FREQ:FIX {} MHz".format(freq + 0.3))
            time.sleep(.5)
            print("Freq: {} Avg Gain: {}".format(freq, self.getAvgGain()))
            freq += 1

    def calibration(self):
        self.getFirstMinimun()
        return

        steepList = (40, 20, 15, 10, 5, 1)
        loopStart = self.config.getConfAttr('settings', 'loopstart')
        self.getFase.set_text(loopStart)
        self.setFaseBtn.Click()
        self.getAmpl.set_text(loopStart)
        self.setAmplBtn.Click()
        time.sleep(1)
        self.minGain.update({'FaseData': self.getFase.texts()[0],
                             'AmplData': self.getAmpl.texts()[0],
                             'Gain': self.getAvgGain()})
        self.pbar = ProgressBar(maxval=len(steepList) * 49)
        self.pb = 0
        self.pbar.start()
        for p, n in enumerate(steepList):
            time.sleep(.5)
            self.setFase(n)
            self.setAmplitude(n)
            if max(self.getGainList()) < float(self.parent.limitsAmpl.get('l2_limit')):
                status = True
            else:
                status = False
        self.pbar.finish()
        print('\nAvg gain: {}'.format(self.getAvgGain()))
        print('Max marker: {}'.format(max(self.getGainList())))
        if status:
            print('Loop2 complete')
        else:
            print('Loop2 incomplete')

        self.gen1.write(":OUTP:STAT OFF")
        self.gen2.write(":OUTP:STAT OFF")
        raw_input('Press enter for continue...')

    def setFase(self, steep):
        oldGain = self.getAvgGain()
        loopCount = 7
        direction = 1
        self.scrollFase.set_focus()
        while True:
            self.printCurrentMin()
            self.scrollFase.wheel_mouse_input(wheel_dist=steep * direction)
            currGain = self.getAvgGain()
            if currGain < self.minGain.get('Gain'):
                self.minGain.update({'FaseData': self.getFase.texts()[0],
                                     'AmplData': self.getAmpl.texts()[0],
                                     'Gain': currGain})
            if currGain > oldGain:
                direction *= -1
                loopCount -= 1
                if loopCount == 0:
                    self.getFase.set_text(self.minGain.get('FaseData'))
                    self.setFaseBtn.Click()
                    return
            oldGain = currGain

    def setAmplitude(self, steep):
        oldGain = self.getAvgGain()
        loopCount = 7
        direction = 1
        self.scrollAmpl.set_focus()
        while True:
            self.printCurrentMin()
            self.scrollAmpl.wheel_mouse_input(wheel_dist=steep * direction)
            currGain = self.getAvgGain()
            if currGain < self.minGain.get('Gain'):
                self.minGain.update({'FaseData': self.getFase.texts()[0],
                                     'AmplData': self.getAmpl.texts()[0],
                                     'Gain': currGain})
            if currGain > oldGain:
                direction *= -1
                loopCount -= 1
                if loopCount == 0:
                    self.getAmpl.set_text(self.minGain.get('AmplData'))
                    self.setAmplBtn.Click()
                    return
            oldGain = currGain

    def getGainList(self):
        gainList = []
        for i in xrange(len(self.markFreqList)):
            gain = self.sa.query("CALC:MARK{}:Y?".format(i + 1))
            gainList.append(round(float(gain), 2))
        return gainList

    def getAvgGain(self):
        gainList = self.getGainList()
        return round(sum(gainList)/len(gainList), 2)

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

    def printCurrentMin(self):
        # stdout.write('\rCurrent minimum - Fase: {} Ampl: {} Avg gain: {}'.format(self.minGain.get('FaseData'),
        #                                                                          self.minGain.get('AmplData'),
        #                                                                          self.minGain.get('Gain')))
        # stdout.flush()
        self.pb += 1
        self.pbar.update(self.pb)

