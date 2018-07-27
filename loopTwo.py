import time
from config import Config
from progressbar import ProgressBar


class LoopTwo:
    def __init__(self, mainProg, node):
        self.Wnd_Node = node
        self.parent = mainProg
        self.config = Config(mainProg)
        self.instrument = self.parent.instrument

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

        self.sa = self.instrument.saPreset(freq=self.center, line=self.harmonyLimit)
        self.gen1, self.gen2 = self.instrument.genPreset(freq=self.center)

        if node is not None:
            self.calibration()

    def setMinimum(self):
        self.getFase.set_text(self.minGain.get('FaseData'))
        self.setFaseBtn.Click()
        self.getAmpl.set_text(self.minGain.get('AmplData'))
        self.setAmplBtn.Click()

    def setMarkers(self, freq):
        self.markFreqList = (freq - .9, freq + .9)
        for i, freq in enumerate(self.markFreqList):
            i += 1
            self.sa.write(":CALC:MARK{}:STAT ON".format(i))
            self.sa.write(":CALC:MARK{}:X {} MHz".format(i, self.markFreqList[i - 1]))

    def calibration(self):
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
        pbar = ProgressBar(maxval=256)
        pbar.start()
        while rSteep >= 1:
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
            fBeg = self.minGain.get('FaseData') - rSteep*2
            fEnd = self.minGain.get('FaseData') + rSteep*2

            aBeg = self.minGain.get('AmplData') - rSteep*2
            aEnd = self.minGain.get('AmplData') + rSteep*2
            if fBeg < absMin:
                fBeg = absMin
            if fEnd > absMax:
                fEnd = absMax
            if aBeg < absMin:
                aBeg = absMin
            if aEnd > absMax:
                aEnd = absMax
        pbar.finish()

        print('\nAvg gain: {}'.format(self.getAvgGain()))
        print('Max harmony: {}'.format(max(self.getGainList())))
        if max(self.getGainList()) < float(self.parent.limitsAmpl.get('l2_limit')):
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
        self.sa.write("DISP:WIND:TRAC:Y:RLEV:OFFS {}".format(self.instrument.getOffset(freq=self.center)))
        genList = (self.gen1, self.gen2)
        for curGen, freq in enumerate([self.center - 0.3, self.center + 0.3]):
            self.sa.write(":CALC:MARK1:STAT ON")
            self.sa.write(":CALC:MARK1:X {} MHz".format(freq))
            gen = genList[curGen]
            gen.write(":FREQ:FIX {} MHz".format(freq))
            gen.write("POW:AMPL -20 dBm")
            gen.write(":OUTP:STAT ON")
            time.sleep(1)
            self.instrument.setGainTo(nGen=curGen + 1, need=need)
            gen.write(":OUTP:STAT OFF")
        self.gen1.write(":OUTP:STAT ON")
        self.gen2.write(":OUTP:STAT ON")


