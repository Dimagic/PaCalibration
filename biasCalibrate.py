import pywinauto

from config import Config
from instrument import Instrument


class BiasCalibrate:
    def __init__(self, node):
        self.Wnd_Node = node
        self.vg1 = self.Wnd_Node.Edit6
        self.setVg1 = self.Wnd_Node.Set6
        self.vg2 = self.Wnd_Node.Edit5
        self.setVg2 = self.Wnd_Node.Set5
        self.instr = Instrument()
        print(self.instr.getInstr(Config.getConfAttr('instruments', 'mt').query('*IDN?')))
        # self.calibration()

    def calibration(self):
        for i in xrange(0, 501):
            self.vg1.set_text(str(i))
            self.Wnd_Node.Wait('ready')
        for i in xrange(0, 501):
            self.vg2.set_text(str(i))
            self.Wnd_Node.Wait('ready')

