from config import Config
from instrument import Instrument


class LoopOne:
    def __init__(self, mainProg, node):
        self.Wnd_Node = node
        self.parent = mainProg
        self.config = Config(mainProg)
        self.na = Instrument(mainProg).getInstr(self.config.getConfAttr('instruments', 'na'))
        # self.scrollFase = self.Wnd_Node.TTrackBar4
        # self.scrollAmpl = self.Wnd_Node.TTrackBar3
        # self.setFase = self.Wnd_Node.Set4
        # self.setAmpl = self.Wnd_Node.Set3
        self.naPreset()

    def naPreset(self): #pa00036/aaaa
        span = self.parent.limitsAmpl.get('freqstop') - self.parent.limitsAmpl.get('freqstart')
        center = self.parent.limitsAmpl.get('freqstart') + span/2
        self.na.write(":SYST:PRES")
        self.na.write(":SENS1:FREQ:CENT {}E6".format(center))
        self.na.write(":SENS1:FREQ:SPAN {}E6".format(span))
        self.na.write(":SOUR1:POW:ATT 40")
        self.na.write(":SOUR1:POW:PORT2 -45")
        self.na.write(":CALC1:PAR1:DEF S12")
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
        print(self.getGainList())
        print(self.getAvgGain())

    def calibration(self):
        self.setFase(self.getAvgGain())

    def setFase(self, oldGain):
        retryCount = 10
        steep = 1
        direction = 1
        while True:
            self.scrollFase.wheel_mouse_input(wheel_dist=steep * direction)
            currGain = self.getAvgGain()
            if currGain > oldGain:
                direction *= -1
                oldGain = currGain
                retryCount -= 1
                if retryCount == 0:
                    self.setAmplitude(currGain)
            if currGain < 38:
                break

    def setAmplitude(self, oldGain):
        retryCount = 10
        steep = 1
        direction = 1
        while True:
            self.scrollAmpl.wheel_mouse_input(wheel_dist=steep * direction)
            currGain = self.getAvgGain()
            if currGain > oldGain:
                direction *= -1
                oldGain = currGain
                retryCount -= 1
                if retryCount == 0:
                    self.setAmplitude(currGain)
            if currGain < 38:
                break

    def getGainList(self):
        gainList = []
        for i in xrange(1, 4):
            gain = self.na.query(":CALC1:MARK{}:Y?".format(i)).split(',')[0]
            gainList.append(round(float(gain), 2))
        return gainList

    def getAvgGain(self):
        gainList = self.getGainList()
        return round(sum(gainList)/len(gainList), 2)