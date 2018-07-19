import time
from sys import stdout
from config import Config
from instrument import Instrument


class LoopOne:
    def __init__(self, mainProg, node):
        self.Wnd_Node = node
        self.parent = mainProg
        self.config = Config(mainProg)
        self.na = Instrument(mainProg).getInstr(self.config.getConfAttr('instruments', 'na'))
        self.scrollFase = self.Wnd_Node.TTrackBar4
        self.scrollAmpl = self.Wnd_Node.TTrackBar3
        self.setFaseBtn = self.Wnd_Node.Set4
        self.setAmplBtn = self.Wnd_Node.Set3
        self.getFase = self.Wnd_Node.Edit4
        self.getAmpl = self.Wnd_Node.Edit3
        self.minGain = {}
        self.naPreset()

    def naPreset(self):
        span = self.parent.limitsAmpl.get('freqstop') - self.parent.limitsAmpl.get('freqstart')
        center = self.parent.limitsAmpl.get('freqstart') + span/2
        self.na.write(":SYST:PRES")
        self.na.write(":SENS1:FREQ:CENT {}E6".format(center))
        self.na.write(":SENS1:FREQ:SPAN {}E6".format(span))
        self.na.write(":SOUR1:POW:ATT 40")
        self.na.write(":SOUR1:POW:PORT1 -45")
        self.na.write(":CALC1:PAR1:DEF S21")
        self.na.write(":SENS1:SWE:POIN 1601")
        try:
            peakCount = int(self.config.getConfAttr('settings', 'peakcount'))
            start = float(self.parent.limitsAmpl.get('freqstart'))
            for i in xrange(peakCount):
                i += 1
                steepFreq = float(span/(peakCount - 1))
                self.na.write(":CALC1:MARK{} ON".format(i))
                self.na.write(":CALC1:MARK{}:X {}E6".format(i, start + steepFreq * (i - 1)))
        except Exception as e:
            print("Initialisation network error, check config file:")
            raw_input(str(e))
            self.parent.mainMenu()
        time.sleep(3)
        self.calibration()

    def calibration(self):
        steepList = (20, 15, 10, 5, 1)
        loopStart = self.config.getConfAttr('settings', 'loopstart')
        self.getFase.set_text(loopStart)
        self.setFaseBtn.Click()
        self.getAmpl.set_text(loopStart)
        self.setAmplBtn.Click()
        self.minGain.update({'FaseData': self.getFase.texts()[0],
                             'AmplData': self.getAmpl.texts()[0],
                             'Gain': self.getAvgGain()})
        for n in steepList:
            self.setFase(n)
            self.setAmplitude(n)
            if max(self.getGainList()) < float(self.parent.limitsAmpl.get('l1_limit')):
                status = True
            else:
                status = False
        print('\nAvg gain: {}'.format(self.getAvgGain()))
        print('Max marker: {}'.format(max(self.getGainList())))
        if status:
            raw_input('Loop1 complete. Press enter for continue...')
        else:
            raw_input('Loop1 incomplete. Press enter for continue...')
        self.parent.mainMenu()

    def setFase(self, steep):
        oldGain = self.minGain.get('Gain')
        loopCount = 15
        direction = 1
        self.scrollFase.set_focus()
        while True:
            self.printCurrentMin()
            self.scrollFase.wheel_mouse_input(wheel_dist=steep * direction)
            currGain = self.getAvgGain()
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
            if currGain < -38:
                return True

    def setAmplitude(self, steep):
        oldGain = self.minGain.get('Gain')
        loopCount = 15
        direction = 1
        self.scrollAmpl.set_focus()
        while True:
            self.printCurrentMin()
            self.scrollAmpl.wheel_mouse_input(wheel_dist=steep * direction)
            currGain = self.getAvgGain()
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
            if currGain < -38:
                return True

    def getGainList(self):
        gainList = []
        for i in xrange(1, int(self.config.getConfAttr('settings', 'peakcount')) + 1):
            gain = self.na.query(":CALC1:MARK{}:Y?".format(i)).split(',')[0]
            gainList.append(round(float(gain), 2))
        return gainList

    def getAvgGain(self):
        gainList = self.getGainList()
        return round(sum(gainList)/len(gainList), 2)

    def printCurrentMin(self):
        stdout.write('\rCurrent minimum - Fase: {} Ampl: {} Avg gain: {}'.format(self.minGain.get('FaseData'),
                                                                                 self.minGain.get('AmplData'),
                                                                                 self.minGain.get('Gain')))
