from sys import stdout
from config import Config
from instrument import Instrument


class BiasCalibrate:
    def __init__(self, mainProg, node):
        self.Wnd_Node = node
        self.parent = mainProg
        self.config = Config(mainProg)
        self.vg1 = self.Wnd_Node.Edit6
        self.vg2 = self.Wnd_Node.Edit5
        self.offVg1 = self.Wnd_Node.Off2
        self.offVg2 = self.Wnd_Node.Off
        self.setVg1 = self.Wnd_Node.Set6
        self.setVg2 = self.Wnd_Node.Set5
        self.scrollVg1 = self.Wnd_Node.TTrackBar6
        self.scrollVg2 = self.Wnd_Node.TTrackBar5
        self.instr = Instrument(mainProg)
        self.prePostCalibration()
        self.calibration(1)
        self.calibration(2)
        self.prePostCalibration()

    def prePostCalibration(self):
        self.offVg1.Click()
        self.offVg2.Click()
        self.setVg1.Click()
        self.setVg2.Click()

    def calibration(self, fase):
        if fase == 1:
            scroll = self.scrollVg1
            vgEdit = self.vg1
            set = self.setVg1
            off = self.offVg1
        else:
            scroll = self.scrollVg2
            vgEdit = self.vg2
            set = self.setVg2
            off = self.offVg2
        try:
            multi = self.instr.getInstr(self.config.getConfAttr('instruments', 'mt'))
            multi.write('*CLS')
            multi.write('CONF:CURRENT:DC')
        except Exception as e:
            raw_input(str(e))
        start = self.getCurrent(multi)
        off.Click()
        vgEdit.set_text(self.config.getConfAttr('settings', 'vgstart'))
        set.Click()
        if (self.getCurrent(multi) - start) <= self.parent.limitsAmpl.get('bias'):
            direction = False
        else:
            direction = True
        scroll.set_focus()
        # direction = self.getDirrection(start, multi, scroll)
        delta = 0
        while True:
            count = int((self.parent.limitsAmpl.get('bias') - delta)//5)
            if count == 0:
                count = 1
            if direction:
                steep = 1 * count
            else:
                steep = -1 * count
            scroll.wheel_mouse_input(wheel_dist=steep)
            delta = round(self.getCurrent(multi) - start, 2)
            stdout.write('\rBIAS VG{}: {}'.format(fase, delta))
            stdout.flush()
            if ((delta >= self.parent.limitsAmpl.get('bias') - self.parent.limitsAmpl.get('biaslimits')) \
                    and (delta <= self.parent.limitsAmpl.get('bias') + self.parent.limitsAmpl.get('biaslimits'))):
                break
            if vgEdit.texts()[0] > self.config.getConfAttr('settings', 'vglimit'):
                break
            if delta > self.parent.limitsAmpl.get('bias') + 10:
                raw_input('\nValue VG{} not found. Press enter for restart...'.format(fase))
                self.calibration(fase)

        print
        off.Click()
        set.Click()

    def getCurrent(self, multi):
        return abs(float(multi.query('MEAS:CURR:DC?'))*1000)


