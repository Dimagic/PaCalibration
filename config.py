import configparser


class Config:
    def __init__(self, parent):
        self.parent = parent
        self.config = configparser.ConfigParser()
        self.configFile = './config.ini'
        self.config.read(self.configFile, encoding='utf-8-sig')

    def getConfAttr(self, blockName, attrName):
        try:
            self.config.read(self.configFile, encoding='utf-8-sig')
            return self.config.get(blockName, attrName)
        except Exception as e:
            print('ERROR: {}'.format(str(e)))
            raw_input("Press enter to continue...")
            self.parent.mainMenu()

    def setConfAttr(self, section, system, value):
        self.config.read(self.configFile)
        cfgfile = open(self.configFile, 'w')
        self.config.set(section, system, value)
        self.config.write(cfgfile)
        cfgfile.close()
