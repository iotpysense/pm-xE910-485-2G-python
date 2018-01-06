import MDM
import time
import SER
import USB0

def CRLF():
    USB0.send('\r\n')
    
def USB0_receive(timeout):
    res = ''
    start = time.time()
    while (time.time() - start < timeout):
        res = res + USB0.read()
    return res

def MDM_receive(timeout):
    try:
        res = ''
        start = time.time()
        while (time.time() - start < timeout):
            res = res + MDM.read()
        return res
    except Exception as e:
        USB0.send('FATAL ERROR: utils.MDM_receive(): {}\r\n'.format(e))
        
def SER_receive(timeout):
    try:
        res = ''
        start = time.time()
        while (time.time() - start < timeout):
            res = res + SER.read()
        return res
    except Exception as e:
        USB0.send('FATAL ERROR: utils.SER_receive(): {}\r\n'.format(e))

### GSM HELPER FUNCTIONS ###

def get_CPIN():
    try:
        MDM.send('AT+CPIN?\r', 0)
        res = MDM_receive(2)
        if res.find('OK') != -1:
            return (1,)
        else:
            return (-1,)
    except Exception as e:
        USB0.send('FATAL ERROR: utils.getcpin(): {}\r\n'.format(e))
        
def set_APN(apn):
    MDM.send('AT+CGDCONT=1,"IP","{}"\r'.format(apn), 0)
    res = MDM_receive(2)
    if res.find('OK') != -1:
        return (1,)
    else:
        return (-1,)

def get_SGACT():
    try:
        MDM.send('AT#SGACT?\r', 0)
        s = MDM_receive(5)
        
        if s.find('OK') != -1:
            x = s.find(',')
            a = s[x-1]
            b = s[x+1]
            return (1, int(a), int(b), s) 
        else:
            return (-1, s)
    except Exception as e:
        USB0.send('FATAL ERROR: utils.get_SGACT(): {}\r\n'.format(e))
        
def set_SGACT(val1, val2):
    try:
        MDM.send('AT#SGACT={},{}\r'.format(val1, val2), 0)
        s = MDM_receive(20) 
        if s.find('OK') != -1:
            return (1, s)
        else:
            return (-1, s)
    except Exception as e:
        USB0.send('FATAL ERROR: utils.set_SGACT(): {}\r\n'.format(e))

def get_DWCONN():
    try:
        MDM.send('AT#DWCONN?\r', 0)
        s = MDM_receive(10)
        
        if s.find('OK') != -1:
            x = s.find(',')
            a = s[x-1]
            b = s[x+1]
            return (1, int(a), int(b), s)
        else:
            return (-1, s)
    except Exception as e:
        USB0.send('FATAL ERROR: utils.get_DWCONN(): {}\r\n'.format(e))
        
def set_DWCONN(val):
    try:
        MDM.send('AT#DWCONN={}\r'.format(val), 0)
        s = MDM_receive(10) 
        if s.find('OK') != -1:
            return (1,)
        else:
            return (-1,)
    except Exception as e:
        USB0.send('FATAL ERROR: utils.set_DWCONN(): {}\r\n'.format(e))
    
### MQTT HELPER FUNCTIONS ###

def set_DWCFG(endpoint, token):
    MDM.send('AT#DWCFG={},0,{}\r'.format(endpoint, token), 0)
    res = MDM_receive(2)
    if res.find('OK') != -1:
        return (1,)
    else:
        return (-1,)
    
def set_DWEN():
    MDM.send('AT#DWEN=0,1\r', 0)
    res = MDM_receive(2)
    if res.find('OK') != -1:
        return (1,)
    else:
        return (-1,)
    
def mqtt_disconnect(log=False):
    
    if log: USB0.send('\r\nMQTT Disconnecting START\r\n')
    
    time.sleep(1)
    res = get_CPIN()
    
    if res[0] != -1:
        if log: USB0.send('SIM Ready...OK\r\n')
    else:
        if log: USB0.send('SIM Error...ERROR\r\n')
    try:
        # checking #DWCONN status
        # if #DWCONN=0,0
        res = get_DWCONN()
        
        if res[0] != -1 and res[1]==0 and res[2]==0:
            if log: USB0.send('DWCONN=0,0...OK\r\n')
        
        # if #DWCONN=1,1
        elif res[0] != -1 and res[1]==1 and res[2]==1:
            res = set_DWCONN(0)
            if res[0] != -1:
                if log: USB0.send('DWCONN=0...OK\r\n')
            else:
                if log: USB0.send('DWCONN=0...ERROR\r\n')
        
        # if #DWCONN=1,2
        elif res[0] != -1 and res[1]==1 and res[2]==2:
            res = set_DWCONN(0)
            if res[0] != -1:
                if log: USB0.send('DWCONN=0...OK\r\n')
            else:
                if log: USB0.send('DWCONN=0...ERROR\r\n')
        
        # if #DWCONN=1,3
        elif res[0] != -1 and res[1]==1 and res[2]==3:
            res = set_DWCONN(0)
            if res[0] != -1:
                if log: USB0.send('DWCONN=0...OK\r\n')
            else:
                if log: USB0.send('DWCONN=0...ERROR\r\n')       
                
        else:
            if log: USB0.send('DWCONN=0,0...ERROR\r\n')      
    except Exception as e:
        if log: USB0.send('FATAL ERROR mqtt.disconnect(): {}...ERROR\r\n'.format(e))
        
        time.sleep(1)
        
    try:
        # checking #SGACT status
        # if #SGACT=1,0
        res = get_SGACT()
        if res[0] != -1 and res[1]==1 and res[2]==0:
            if log: USB0.send('SGACT=1,0...OK\r\n')
        
        # if #SGACT=1,1
        elif res[0] != -1 and res[1]==1 and res[2]==1:
            res = set_SGACT(1,0)
            if res[0] != -1:     
                
                if log: USB0.send('SGACT=1,0...OK\r\n')
            else:
                if log: USB0.send('SGACT=1,0...ERROR\r\n')
        else:
            if log: USB0.send('SGACT=1,0...ERROR\r\n')
    except Exception as e:
        if log: USB0.send('FATAL ERROR mqtt.disconnect(): {}...ERROR\r\n'.format(e))
        
    if log: USB0.send('MQTT Disconnecting STOP\r\n')
    time.sleep(1)
    

def mqtt_connect(log=False):
    
    if log: USB0.send('\r\nMQTT Connecting START\r\n')
    
    time.sleep(1)
    res = get_CPIN()
    
    if res[0] != -1:
        if log: USB0.send('SIM Ready...OK\r\n')
    else:
        if log: USB0.send('SIM Error...ERROR\r\n')
    
    try:
        res = get_SGACT()
        if res[0] != -1 and (res[1]==1 and res[2]==1):
            if log: USB0.send('SGACT=1,1...OK\r\n')
        elif res[0] != -1 and (res[1]==1 and res[2]==0):
            res = set_SGACT(1,1)
            if res[0] != -1:     
                if log: USB0.send('SGACT=1,1...OK\r\n')
            else:
                if log: USB0.send('SGACT=1,1...ERROR\r\n')
        else:
            if log: USB0.send('SGACT=1,1...ERROR\r\n')
    except Exception as e:
        if log: USB0.send('FATAL ERROR mqtt.connect(): {}...ERROR\r\n'.format(e))
            
    try:
        res = get_DWCONN()
        if res[0] != -1 and ((res[1]==1 and res[2]==2)):
            if log: USB0.send('DWCONN=1,2...OK\r\n')
        elif res[0] != -1 and ((res[1]==1 and res[2]==1) or (res[1]==1 and res[2]==3)):
            res = set_DWCONN(0)
            if res[0] != -1:
                res = set_DWCONN(1)
                if res[0] != -1:
                    if log: USB0.send('DWCONN=1,2...OK\r\n')
                else:
                    if log: USB0.send('DWCONN=1,2...ERROR\r\n')
        elif res[0] != -1 and (res[1]==0 and res[2]==0):
            res = set_DWCONN(1)
            if res[0] != -1:
                if log: USB0.send('DWCONN=1...OK\r\n')
            else:
                if log: USB0.send('DWCONN=1...ERROR\r\n')  
        else:
            if log: USB0.send('DWCONN=1...ERROR\r\n')      
    except Exception as e:
        if log: USB0.send('FATAL ERROR mqtt.connect(): {}...ERROR\r\n'.format(e))
        
        time.sleep(1)
        
    if log: USB0.send('MQTT Connecting STOP\r\n')
    time.sleep(1)
    
def mqtt_send(a, b):
    try:
        MDM.send('AT#DWSEND=0,property.publish,key,{},value,{}\r'.format(a, b), 0)
        ser = MDM_receive(4)
        if ser.find('OK') != -1:
            USB0.send('MQTT message sent\r\n')
        else:
            USB0.send('ERROR in MQTT message sending\r\n')
            
    except Exception as e:
        USB0.send('FATAL ERROR: utils.mqtt_send(): {}\r\n'.format(e))
        

def get_TIME():
    try: 
        MDM.send('AT#CCLK?\r', 0)
        res = MDM_receive(0.5)
        if res.find('OK') != -1:
            x = res.find('"')+1
            y = res.find(',')
            _cdate = res[x:y]
            x = y+1
            y = res.find('+')
            _ctime = res[x:y]
            return (1,_cdate,_ctime)
        else:
            return (-1,)
    except Exception as e:
        USB0.send('FATAL ERROR: utils.get_TIME(): {}\r\n'.format(e))
        
def get_CSQ():
    try:
        MDM.send('AT+CSQ\r', 0)
        res = MDM_receive(2)
        if res.find('OK') != -1:
            x = res.find(':')
            y = res.find(',')
            z = res[x+2:y]
            return (1, z)
        else:
            return (-1,)
    except Exception as e:
        USB0.send('FATAL ERROR: utils.get_CSQ(): {}\r\n'.format(e))
        