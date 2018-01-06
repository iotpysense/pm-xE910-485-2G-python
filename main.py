import MDM
import USB0
import SER

import time
import sys

LOG_TO_USB0 = True

try:
    import utils
    import stm32
    import fif
    import config
    from logger import log
except Exception as e:
    if LOG_TO_USB0: USB0.send('FATAL ERROR IMPORT: {}\r\n...ERROR'.format(e))

class USBWriter():
    def write(self, s):
        USB0.send(s+'r')
        
class LOGWriter():
    def write(self, s):
        log(s+'r')
        
sys.stdout = sys.stderr = LOGWriter()

log('Program Started')

CONFIG = config.Config()
CONFIG.read()

CONF_APN = CONFIG.get('APN')
CONF_MQTT_ENDPOINT = CONFIG.get('MQTT_ENDPOINT')
CONF_MQTT_TOKEN = CONFIG.get('MQTT_TOKEN')
CONF_METER_TO_READ = CONFIG.get('METER_TO_READ').split(',')
CONF_READ_TIMEOUT = int(CONFIG.get('READ_TIMEOUT'))
CONF_WATCHDOG_TIMEOUT = int(CONFIG.get('WATCHDOG_TIMEOUT'))
CONF_WATCHDOG_RESET = int(CONFIG.get('WATCHDOG_RESET'))

SW_VER = '0.6'

__STM = stm32.STM32(usb_log=True)
__FIF = fif.FIF(__STM, usb_log=True)


def modem_init():

    try:
        global __STM
        __STM.set_wdg(CONF_WATCHDOG_TIMEOUT)
        
        __STM.set_led('RED','OFF',0)
        __STM.set_led('YELLOW','OFF',0)
        __STM.set_led('BLUE','OFF',0)
        __STM.set_led('GREEN','OFF',0)
        time.sleep(0.5)
        __STM.set_led_toggle('RED',1000,5,5)
        # add checking OK b sometimes LEDs are not set up
    except Exception as e:
        USB0.send('FATAL ERROR: __STM: {}\r\n'.format(e))
        log('FATAL ERROR: __STM: {}\r\n'.format(e))

    utils.CRLF()
    USB0.send('\r\n2017 (c) PySENSE RS485 SW VER: {}\r\n'.format(SW_VER))

    try:
        s = utils.set_APN(CONF_APN)
        if s[0]:
            USB0.send('Setting APN:{}...OK\r\n'.format(CONF_APN))
        else:
            USB0.send('Setting APN...ERROR\r\n')
    except Exception as e:
        if LOG_TO_USB0: 
            USB0.send('FATAL ERROR main.MODEM_INIT() -> set_APN(): {}...ERROR\r\n'.format(e))
            log('FATAL ERROR main.MODEM_INIT() -> set_APN(): {}...ERROR\r\n'.format(e))
    try:
        s = utils.set_DWCFG(CONF_MQTT_ENDPOINT, CONF_MQTT_TOKEN)
        if s[0]:
            USB0.send('Setting DWCFG...OK\r\n')
        else:
            USB0.send('Setting DWCFG...ERROR\r\n')
    except Exception as e:
        if LOG_TO_USB0:
            USB0.send('FATAL ERROR main.MODEM_INIT() -> set_DWCFG(): {}...ERROR\r\n'.format(e))
            log('FATAL ERROR main.MODEM_INIT() -> set_DWCFG(): {}...ERROR\r\n'.format(e))
    try:
        s = utils.set_DWEN()
        if s[0]:
            USB0.send('Setting DWEN...OK\r\n')
        else:
            USB0.send('Setting DWEN...ERROR\r\n')
    except Exception as e:
        if LOG_TO_USB0:
            USB0.send('FATAL ERROR main.MODEM_INIT() -> set_DWEN(): {}...ERROR\r\n'.format(e))
            log('FATAL ERROR main.MODEM_INIT() -> set_DWEN(): {}...ERROR\r\n'.format(e))
    
    utils.mqtt_disconnect(log=True)
    
    __STM.set_led('RED','ON',100)
    
    USB0.send('\r\nAT++ INTERPRETER READY\r\n')
    log('modem_init() done ok')
    
    
def main_loop():
    in_ = ''
    out_ = ''

    loop_flag = True
    
    global __STM
    global __FIF
    global CONF_READ_TIMEOUT
    global CONF_METER_TO_READ
    global CONF_WATCHDOG_RESET
    
    start_read = time.time()
    start_wdg = time.time()
    
    try:
        while loop_flag:
            if time.time() - start_wdg > CONF_WATCHDOG_RESET:
                __STM.reset_wdg()
                start_wdg = time.time()
                
            elif time.time() - start_read > CONF_READ_TIMEOUT:
                
                #STM_GO = stm32.STM32()
                #FIF_GO = fif.FIF(STM_GO, usb_log=True)
                __STM.set_led_toggle('YELLOW',1000,1,1)
                
                utils.mqtt_connect(log=True)
                time.sleep(15)
                
                for m in CONF_METER_TO_READ:
                    res = __FIF.read_LE_0xM(int(m))
                    
                    if res[0] != 0:
                        utils.mqtt_send('le_0xm_{}'.format(m), res[9])
                        USB0.send('Meter with {} address read out correctly\r\n'.format(m))
                    else:
                        USB0.send('Meter with {} address is not responding\r\n'.format(m))
                    time.sleep(15)
                
                time.sleep(30)
                utils.mqtt_disconnect(log=True)
                
                __STM.set_led('YELLOW','OFF',0)
                start_read = time.time()
                __STM.reset_wdg()
                start_wdg = time.time()
                continue
                
            elif (in_.find('AT++') == -1):
                in_ = in_ + USB0.read()
            else:
                if (in_.find('AT++') != -1):
            
                    if (in_.find('AT++CONFIG?') != -1):
                        # returns whole configuration
                        CONFIG.dump()
                        USB0.send('++CONFIG OK\r\n')
                        in_ = ''
                        start_read = time.time()
                        continue
                    
                    if (in_.find('AT++METACH=') != -1):
                        # command changes meter addr to new one
                        
                        x = in_.find('=')
                        y = ''
                        for ch in in_[x+1:]:
                            if ch != ',':
                                y += ch
                            else:
                                break
                        addr = y
                        
                        x = in_.find(',')
                        y = ''
                        for ch in in_[x+1:]:
                            if ch != '\r':
                                y += ch
                            else:
                                break
                        new_addr = y
                        try:
                            res = __FIF.change_addr_LE_0xM(int(addr), int(new_addr))
                            USB0.send('METER ADDR CHANGED: {}\r\n'.format(res))
                        except Exception as e:
                             USB0.send('FATAL ERROR ++METACH: {}\r\n'.format(e))
                            
                        USB0.send('++METACH OK\r\n')
                        in_ = ''
                        start_read = time.time()
                        __STM.reset_wdg()
                        start_wdg = time.time()
                        continue
                    
                    
                    if (in_.find('AT++METTR=') != -1):
                        # command sets meters to read out
                        
                        x = in_.find('=')
                        y = in_.find('\r')
                        z = ''
                        for ch in in_[x+1:y]:
                            z += ch
                        
                        CONFIG.set('METER_TO_READ',z)
                        CONFIG.write()
                        CONF_METER_TO_READ = CONFIG.get('METER_TO_READ').split(',')
                        USB0.send('METER_TO_READ -> {}\r\n'.format(CONF_METER_TO_READ))                   
                        USB0.send('++METTR OK\r\n')
                        in_ = ''
                        start_read = time.time()
                        __STM.reset_wdg()
                        start_wdg = time.time()
                        continue
                    
                    if (in_.find('AT++READTM=') != -1):
                        # command sets meters to read out
                        
                        x = in_.find('=')
                        y = in_.find('\r')
                        z = int(in_[x+1:y])
                        
                        CONFIG.set('READ_TIMEOUT',str(z))
                        CONFIG.write()
                        CONF_READ_TIMEOUT = int(CONFIG.get('READ_TIMEOUT'))
                        USB0.send('READ_TIMEOUT -> {}\r\n'.format(CONF_READ_TIMEOUT))                   
                        USB0.send('++READTM OK\r\n')
                        in_ = ''
                        start_read = time.time()
                        __STM.reset_wdg()
                        start_wdg = time.time()
                        continue
            
            
                    if (in_.find('AT++STM?') != -1):
                        USB0.send('++STM OK\r\n')
                        in_ = ''
                        start_read = time.time()
                        __STM.reset_wdg()
                        start_wdg = time.time()
                        continue
            
                    if (in_.find('AT++MQTT=CONNECT') != -1):
                        utils.mqtt_connect(log=True)
                        USB0.send('++STM OK\r\n')
                        in_ = ''
                        start_read = time.time()
                        __STM.reset_wdg()
                        start_wdg = time.time()
                        continue
            
                    if (in_.find('AT++MQTT=DISCONNECT') != -1):
                        utils.mqtt_disconnect(log=True)
                        USB0.send('++STM OK\r\n')
                        in_ = ''
                        start_read = time.time()
                        __STM.reset_wdg()
                        start_wdg = time.time()
                        continue
            
                    if (in_.find('AT++DWCONN') != -1):
                        res = utils.get_DWCONN()
                        USB0.send('{}\r\n'.format(res[0]))
                        USB0.send('++DWCONN OK\r\n')
                        in_ = ''
                        start_read = time.time()
                        __STM.reset_wdg()
                        start_wdg = time.time()
                        continue
          
                    if (in_.find('AT++STM=') != -1):
                
                        cmd_idx = in_.find('=')+1
                        cmd = in_[cmd_idx:]
                
                        SER.send(cmd, 1)
                        res = utils.SER_receive(2)
                        USB0.send('(++STM OK):' + res)
                        in_ = ''
                        start_read = time.time()
                        __STM.reset_wdg()
                        start_wdg = time.time()
                        continue
  
                    if (in_.find('AT++MODEM=') != -1):
                
                        cmd_idx = in_.find('=')+1
                        cmd = in_[cmd_idx:]
                
                        MDM.send(cmd, 1)
                        res = utils.MDM_receive(2)
                        USB0.send('(++MODEM OK):' + res)
                        in_ = ''
                        start_read = time.time()
                        __STM.reset_wdg()
                        start_wdg = time.time()
                        continue
            
                    if (in_.find('AT++QUIT') != -1):
                        __STM.set_led('RED','OFF',0)
                        USB0.send('++QUIT OK\r\n')
                        in_ = ''
                        loop_flag = False
            
                    else:
                        USB0.send('++OK\r\n')
                        in_ = ''
                        start_read = time.time()
                        __STM.reset_wdg()
                        start_wdg = time.time()
                        continue
        else: 
            USB0.send('MODBUS program has been closed...\r\n')
    except Exception as e:
        USB0.send('FATAL ERROR: main loop {}\r\n'.format(e))
        log('FATAL ERROR: main loop {}\r\n'.format(e))

if __name__ == '__main__':
    
    modem_init()
    main_loop()


        

        
        
        
        