import os
import pywinauto
from pywinauto import Application
from pywinauto.controls.win32_controls import ComboBoxWrapper, ButtonWrapper, ListBoxWrapper
from pywinauto.timings import Timings
import time

from config import Config


class Test5:
    def __init__(self, mainProg):
        wk_dir = os.path.dirname(os.path.realpath('__file__'))
        Timings.window_find_timeout = 5
        self.conf = Config(mainProg)
        self.parent = mainProg
        self.mainApp = None
        self.Wnd_NodeEdit = None
        # GENERAL settings
        self.test5Path = wk_dir + '\\test5\\test5.exe'
        self.connectBtn = 'Button8'
        self.addNodeBtn = 'Button2'
        self.listNodes = 'ListBox'
        self.openNodeBtn = 'Open'
        self.tuneChkBox = 'Tune'
        self.readNodeBtn = 'Button16'
        # BIAS settings
        self.vg1OnOff = 'Off2'
        self.vg2OnOff = 'Off'
        self.vg1Set = 'Set6'
        self.vg2Set = 'Set5'
        self.vg1Edit = 'Edit6'
        self.vg2Edit = 'Edit5'
        # 1ST LOOP Settings
        self.loop1PhaseSet = 'Set4'
        self.loop1AmplSet = 'Set3'
        self.loop1PhaseEdit = 'Edit4'
        self.loop1AmplEdit = 'Edit3'
        # 2ST LOOP Settings
        self.loop2PhaseSet = 'Set2'
        self.loop2AmplSet = 'Set'
        self.loop2PhaseEdit = 'Edit2'
        self.loop2AmplEdit = 'Edit'

        self.startTest5()

    def startTest5(self):
        try:
            self.mainApp = Application().Start(self.test5Path)
            self.Wnd_Main = self.mainApp.TForm1
            self.Wnd_Main.Wait('ready')
            self.Wnd_Main.MenuItem(u'&Options...').Click()
            appOptions = Application().Connect(title=u'Options', class_name='TFormOptions')
            Wnd_Options = appOptions.Options
            Wnd_Options.Wait('ready')
            Wnd_Options.RS232.Click()
            Wnd_Options.Close()
            self.Wnd_Main.MenuItem(u'&ComPorts...').Click()
            appPort = Application().Connect(title=u'Port Settings', class_name='TFormComPorts')
            Wnd_Port = appPort[u'Port Settings']
            Wnd_Port.Wait('ready')
            Wnd_Port[u'{}'.format(self.conf.getConfAttr('settings', 'comPort'))].Click()
            Wnd_Port[u'{}'.format(self.conf.getConfAttr('settings', 'baud'))].Click()
            Wnd_Port.Close()
            return self.Wnd_Main
        except Exception as e:
            print('startTest5 ERROR: {}'.format(str(e)))
            return

    def connectAddNode(self):
        try:
            self.Wnd_Main[u'{}'.format(self.addNodeBtn)].Click()
            app = Application().Connect(title=u'Add Node...', class_name='TConnectWiz')
            Wnd_Node = app.TConnectWiz
            Wnd_Node.Wait('ready')
            Wnd_Node.SetFocus()
            Wnd_Node.TypeKeys("{RIGHT}")
            Wnd_Node[u'PnP'].Click()
            time.sleep(1)
            listBox = ListBoxWrapper(Wnd_Node.ListBox.WrapperObject())
            # print('ListBox = {}'.format(listBox.ItemCount()))
            if listBox.ItemCount() == 0:
                self.mainApp.kill_()
                raw_input("Error: Nodes not found. Press enter for continue...")
                self.parent.mainMenu()
            else:
                self.connectNode(Wnd_Node, listBox.ItemTexts()[0])
        except Exception as e:
            print('Error: {}'.format(str(e)))

    def connectNode(self, Wnd_Node, nodeName):
        try:
            print('Node name: {}'.format(nodeName.decode('utf-8')))
            Wnd_Node.Open.Click()
            time.sleep(1)
            app = Application().connect(class_name='TFormNode')
            Wnd_NodeEdit = app.TFormNode
            Wnd_NodeEdit.SetFocus()
            Wnd_NodeEdit.TypeKeys("{TAB 5}")
            Wnd_NodeEdit.TypeKeys("{LEFT 4}")
            Wnd_NodeEdit[u'Tune'].Click()
            Wnd_NodeEdit[u'Button16'].Click()
            time.sleep(1)
            self.Wnd_NodeEdit = Wnd_NodeEdit
        except Exception as e:
            print('Error: {}'.format(str(e)))

    def test5Connection(self, var):
        connectBtn = self.Wnd_Main[u'{}'.format(self.connectBtn)]
        status = connectBtn.Texts()[0]
        if status == 'Connect' and var == 1:
            connectBtn.Click()
        if status == 'disConnect' and var == 0:
            connectBtn.Click()

    def setVg1(self, val):
        pass

    def getVg1(self):
        return int(self.Wnd_NodeEdit.Edit6.Texts()[0])

    def setVg2(self):
        pass

    def getVg2(self):
        pass