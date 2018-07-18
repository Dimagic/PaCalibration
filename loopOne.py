import time
from config import Config
from instrument import Instrument


class LoopOne:
    def __init__(self, mainProg, node):
        print('NODE: {}'.format(node))
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
        self.naPreset()

    def naPreset(self): #pa00036/aaaa
        span = self.parent.limitsAmpl.get('freqstop') - self.parent.limitsAmpl.get('freqstart')
        center = self.parent.limitsAmpl.get('freqstart') + span/2
        self.na.write(":SYST:PRES")
        self.na.write(":SENS1:FREQ:CENT {}E6".format(center))
        self.na.write(":SENS1:FREQ:SPAN {}E6".format(span))
        self.na.write(":SOUR1:POW:ATT 40")
        self.na.write(":SOUR1:POW:PORT1 -45")
        self.na.write(":CALC1:PAR1:DEF S21")
        self.na.write(":SENS1:SWE:POIN 1601")
        self.na.write(":CALC1:MARK1 ON")
        self.na.write(":CALC1:MARK2 ON")
        self.na.write(":CALC1:MARK3 ON")
        self.na.write(":CALC1:MARK4 ON")
        self.na.write(":CALC1:MARK5 ON")
        self.na.write(":CALC1:MARK1:X {}E6".format(center))
        self.na.write(":CALC1:MARK2:X {}E6".format(self.parent.limitsAmpl.get('freqstart')))
        self.na.write(":CALC1:MARK3:X {}E6".format(self.parent.limitsAmpl.get('freqstop')))
        self.na.write(":CALC1:MARK4:X {}E6".format(center - span/4))
        self.na.write(":CALC1:MARK5:X {}E6".format(center + span/4))
        time.sleep(3)
        print(self.getGainList())
        print(self.getAvgGain())
        self.calibration()

    def calibration(self):
        self.setFase(0)

    def setFase(self, oldGain):
        minGain = {'FaseData': self.getFase.texts()[0], 'Gain': self.getAvgGain()}
        loopCount = 10
        steep = 20
        direction = 1
        self.scrollFase.set_focus()
        while True:
            self.scrollFase.wheel_mouse_input(wheel_dist=steep * direction)
            currGain = self.getAvgGain()
            minGain = {'FaseData': self.getFase.texts()[0], 'Gain': currGain}
            if currGain > oldGain:
                direction *= -1
                print(minGain)
                loopCount -= 1
                if loopCount == 0:
                    self.getFase.set_text(minGain.get('FaseData'))
                    self.setFaseBtn.Click()
                    self.setAmplitude(minGain.get('Gain'))
            oldGain = currGain
            if currGain < -38:
                break

    def setAmplitude(self, oldGain):
        minGain = {'AmplData': self.getAmpl.texts()[0], 'Gain': self.getAvgGain()}
        loopCount = 10
        steep = 20
        direction = 1
        self.scrollAmpl.set_focus()
        while True:
            self.scrollAmpl.wheel_mouse_input(wheel_dist=steep * direction)
            currGain = self.getAvgGain()
            minGain = {'AmplData': self.getAmpl.texts()[0], 'Gain': currGain}
            if currGain > oldGain:
                direction *= -1
                print(minGain)
                loopCount -= 1
                if loopCount == 0:
                    raw_input('wwwwwwwwwwww')
                    break
            oldGain = currGain
            if currGain < -38:
                raw_input('done')
                break

    def getGainList(self):
        gainList = []
        for i in xrange(1, 6):
            gain = self.na.query(":CALC1:MARK{}:Y?".format(i)).split(',')[0]
            gainList.append(round(float(gain), 2))
        return gainList

    def getAvgGain(self):
        gainList = self.getGainList()
        return round(sum(gainList)/len(gainList), 2)