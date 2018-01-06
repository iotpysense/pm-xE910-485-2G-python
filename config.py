import USB0

class Config:
    def __init__(self, usb_log=False):
        self.config = {}
        self.__path='./config.ini'
        self.__usb_log = usb_log

        self.__defConf = {
            'APN':'NXT17.NET',
            'MQTT_ENDPOINT':'api-de.devicewise.com',
            'MQTT_TOKEN':'0g9ZO5h0T4OXOsQ2',
            'METER_TO_READ':'1,2,3,4,5',
            'READ_TIMEOUT': '3600',
            'WATCHDOG_TIMEOUT':'900',
            'WATCHDOG_RESET':'300'
        }

    def get(self, k):
        return self.config[k]

    def set(self, k, v):
        self.config[k] = v

    def read(self):
        try:
            fh = open('config.ini', 'r')
            try:
                lines = fh.readlines()
                for l in lines:
                    kv = l.strip().split('::')
                    self.config[kv[0]] = kv[1]
            finally:
                fh.close()
        except IOError:
            if self.__usb_log: USB0.send('FATAL ERROR: Configuration file not found: {}\r\n'.format(e))
            fh = open('config.ini','w')
            try:
                lines = []
                for k in self.__defConf.keys():
                    lines.append(k + '::' + self.__defConf[k] + '\n')
                fh.writelines(lines)
            finally:
                fh.close()
                fh = open('config.ini', 'r')
            try:
                lines = fh.readlines()
                for l in lines:
                    kv = l.strip().split('::')
                    self.config[kv[0]] = kv[1]
            finally:
                fh.close()

    def write(self):
        try:
            fh = open('config.ini', 'w')
            try:
                lines = []
                for k in self.config.keys():
                    lines.append(k + '::' + self.config[k] + '\n')
                fh.writelines(lines)
            finally:
                fh.close()
        except IOError:
            if self.__usb_log: USB0.send('FATAL ERROR: Configuration file not found: {}\r\n'.format(e))

    def dump(self):
        for k in self.config.keys():
            USB0.send(('{}::{}\r\n'.format(k, self.config[k])))
                      