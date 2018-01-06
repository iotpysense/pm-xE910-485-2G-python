import SER
import USB0

import time


class STM32():

    def __init__(self, bd='115200', sconf='8N1', usb_log=False):
        self.__bd = bd
        self.__sconf = sconf
        self.__usb_log = usb_log
        
        SER.set_speed(self.__bd, self.__sconf)


    def __SER_receive(self, timeout):
        try:
            res = ''
            start = time.time()
            while (time.time() - start < timeout):
                res = res + SER.read()
            return res
        except Exception as e:
            USB0.send('FATAL ERROR: stm32.__SER_receive(): {}\r\n'.format(e))


    def __parseRS485Read(self, resp):
        try:
            if resp.find('OK') != -1:
                temp = resp.find(',')
                x = resp[temp + 1:]
                y = ''
                idx = 0
                for ch in x:
                    if ch != ',':
                        y += ch
                        idx += 1
                    else:
                        break
                bytes_len = int(y)

                x = resp[temp + 1 + idx + 1:]
                y = ''
                
                xc = 0
                while xc < bytes_len:
                    y += x[xc]
                    xc += 1 

                bytes_val = y

                x = resp[temp + 1 + idx + 1 + xc + 1:]
                y = ''
                for ch in x:
                    if ch != ',':
                        y += ch
                    else:
                        break
                crc = y

                return (1, bytes_len, bytes_val, crc)
            else:
                return (-1,)

        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR: {}\r\n'.format(e))


    def __parseRS485Count(self, resp):
        try:
            if resp.find('OK') != -1:
                temp = resp.find(',')
                x = resp[temp + 1:]
                y = ''
                idx = 0
                for ch in x:
                    if ch != ',':
                        y += ch
                        idx += 1
                    else:
                        break
                bytes_count = int(y)

                return (1, bytes_count)
            else:
                return (-1,)

        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR: {}\r\n'.format(e))


    def __parseRS485Flush(self, resp):
        try:
            if resp.find('OK') != -1:
                temp = resp.find(',')
                x = resp[temp + 1:]
                y = ''
                idx = 0
                for ch in x:
                    if ch != ',':
                        y += ch
                        idx += 1
                    else:
                        break
                bytes_flushed = int(y)

                return (1, bytes_flushed)
            else:
                return (-1,)

        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR: {}\r\n'.format(e))


    def __parseRS485Send(self, resp):
        try:
            if resp.find('OK') != -1:
                temp = resp.find(',')
                x = resp[temp + 1:]
                y = ''
                idx = 0
                for ch in x:
                    if ch != ',':
                        y += ch
                        idx += 1
                    else:
                        break
                byte_size = int(y)

                return (1, byte_size)
            else:
                return (-1,)

        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR: {}\r\n'.format(e))


    def __sendRS485Read(self, size, timeout=1):
        try:
            cmd = 'AT+RS485=READ,{}\r'.format(size)
            SER.send(cmd, 0)
            res = self.__SER_receive(timeout)
            return self.__parseRS485Read(res)
        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR: {}\r\n'.format(e))


    def __sendRS485Send(self, len, val, crc=0, timeout=1):
        try:
            cmd = 'AT+RS485=SEND,{},{},{}\r'.format(len, val, crc)
            SER.send(cmd, 0)
            res = self.__SER_receive(timeout)
            return self.__parseRS485Send(res)
        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR: {}\r\n'.format(e))


    def __sendRS485Count(self, timeout=1):
        try:
            cmd = 'AT+RS485=COUNT\r'
            SER.send(cmd, 0)
            res = self.__SER_receive(timeout)
            return self.__parseRS485Count(res)
        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR: {}\r\n'.format(e))


    def __sendRS485Flush(self, size=6000, timeout=1):
        try:
            cmd = 'AT+RS485=FLUSH,{}\r'.format(size)
            SER.send(cmd, 0)
            res = self.__SER_receive(timeout)
            return self.__parseRS485Flush(res)
        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR: {}\r\n'.format(e))
            
            
    def flush_rx_buffer(self, f_size=6000, res_timeout=0.5, max_tries=5, t_timeout=0.5):
        '''Function flushes n bytes in RS485 RX buffer

        :param f_size (int): number of bytes to flush
        :param res_timeout (float): response timeout
        :param max_tries (int): maximum tries number
        :param t_timeout (float): timeout between tries
        :param usb_log (boolean): log to USB interface

        :return (tuple):
        '''
        res_c = 0
        tries = 1
        try:
            while (res_c < 1) and (tries <= max_tries):
                res = self.__sendRS485Flush(f_size, res_timeout)
                res_c = res[0]
                if res[0] != -1:
                    if self.__usb_log: USB0.send('FLUSH OK: {} tries: {}\r\n'.format(res, tries))
                    return res + (tries,)  # -> tuple(1, message, tries)
                    break
                else:
                    time.sleep(t_timeout)
                    tries += 1
                    continue
            else:
                if self.__usb_log: USB0.send('FLUSH ERROR: max {} tries were made\r\n'.format(tries))
                return (-1, tries)  # -> tuple(-1, tries)
        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR flush_rx_buffer(): {}\r\n'.format(e))
            
            
    def count_rx_buffer(self, res_timeout=0.5, max_tries=5, t_timeout=0.5, usb_log=True):
        '''Function returns number of bytes in RS485 RX buffer
    
        :param res_timeout (float): response timeout
        :param max_tries (int): maxium tries number
        :param t_timeout (float): timeout between tries
        :param usb_log (boolean): log to USB interface
        
        :return (tuple):
        '''
        res_c = 0
        tries = 1
        try:
            while (res_c < 1) and (tries <= max_tries):
                res = self.__sendRS485Count(res_timeout)
                res_c = res[0]
                if res[0] != -1:
                    if self.__usb_log: USB0.send('COUNT OK: {} tries: {}\r\n'.format(res, tries))
                    return res + (tries,) # -> tuple(1, count, tries)
                    break
                else:
                    time.sleep(t_timeout)
                    tries += 1
                    continue
            else:
                if self.__usb_log: USB0.send('COUNT ERROR: max {} tries were made\r\n'.format(tries))
                return(-1, tries) # -> tuple(-1, tries)
        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR count_rx_buffer(): {}\r\n'.format(e))
            
    
    def send_totx_buffer(self, value, len, crc='0', res_timeout=0.5, max_tries=5, t_timeout=0.5, usb_log=True):
        '''Function returns number of bytes in RS485 RX buffer
        
        :param value (str): value to send in string format (bytes converted to string format)
        :param value (int): number of chars in value string
        :param crc (str): crc of value in string format (bytes converted to string format)
        :param res_timeout (float): response timeout
        :param max_tries (int): maxium tries number
        :param t_timeout (float): timeout between tries
        :param usb_log (boolean): log to USB interface
        
        :return (tuple):
        '''
        res_c = 0
        tries = 1
        try:
            while (res_c < 1) and (tries <= max_tries):
                res = self.__sendRS485Send(len, value, crc, res_timeout)
                res_c = res[0]
                if res[0] != -1:
                    if self.__usb_log: USB0.send('SEND OK: {} tries: {}\r\n'.format(res, tries))
                    return res + (tries,) # -> tuple(1, message, tries)
                    break
                else:
                    time.sleep(t_timeout)
                    tries += 1
                    continue
            else:
                if self.__usb_log: USB0.send('SEND ERROR: max {} tries were made\r\n'.format(tries))
                return(-1, tries) # -> tuple(-1, tries)
        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR send_totx_buffer(): {}\r\n'.format(e))
    
    
    def read_rx_buffer(self, size, res_timeout=0.5, max_tries=5, t_timeout=0.5, usb_log=True):
        '''Function reads number of bytes from RS485 RX buffer
        
        :param size (int): number of bytes to read
        :param res_timeout (float): response timeout
        :param max_tries (int): maxium tries number
        :param t_timeout (float): timeout between tries
        :param usb_log (boolean): log to USB interface
        
        :return (tuple):
        '''
        res_c = 0
        tries = 1
        try:
            while (res_c < 1) and (tries <= max_tries):
                res = self.__sendRS485Read(size, res_timeout)
                res_c = res[0]
                if res[0] != -1:
                    if self.__usb_log: USB0.send('READ OK: {} tries: {}\r\n'.format(res, tries))
                    return res + (tries,) # -> tuple(1, message, tries)
                    break
                else:
                    time.sleep(t_timeout)
                    tries += 1
                    continue
            else:
                if self.__usb_log: USB0.send('READ ERROR: max {} tries were made\r\n'.format(tries))
                return(-1, tries) # -> tuple(-1, tries)
        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR read_rx_buffer(): {}\r\n'.format(e))
            
            
    def set_led_toggle(self, color, intensity, time_on, time_off, timeout=1):
        try:
            cmd = 'AT+LED={},TOGGLE,{},{},{}\r'.format(color, intensity, time_on, time_off)
            SER.send(cmd, 0)
            res = self.__SER_receive(timeout)
            if res.find('OK') != -1:
                return (1,)
            else:
                return (0,)
        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR set_led_toggle(): {}\r\n'.format(e))
    
    
    def set_led(self, color, state, intensity, timeout=1):
        try:
            cmd = 'AT+LED={},{},{}\r'.format(color, state, intensity)
            SER.send(cmd, 0)
            res = self.__SER_receive(timeout)
            if res.find('OK') != -1:
                return (1,)
            else:
                return (0,)
        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR: set_led(): {}\r\n'.format(e))
            
            
    def set_wdg(self, interval, timeout=1):
        '''Function sets internal STM32 watchdog
        
        :param interval (int): value in seconds from 30 to 64800 (18 hours). Value -1 or 0 turns off the watchdog.
        :param res_timeout (float): resposne timeout
        
        :return (tuple):
        '''
        try:
            cmd = 'AT+WDG=SET,{}\r'.format(interval)
            SER.send(cmd, 0)
            res = self.__SER_receive(timeout)
            if res.find('OK') != -1:
                return (1,)
            else:
                return (0,)
        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR: set_wdgt(): {}\r\n'.format(e))
           
    def reset_wdg(self, timeout=1):
        '''Function resets STM32 watchdog timer
        
        :return (tuple):
        '''
        try:
            cmd = 'AT+WDG\r'
            SER.send(cmd, 0)
            res = self.__SER_receive(timeout)
            if res.find('OK') != -1:
                return (1,)
            else:
                return (0,)
        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR: reset_wdg(): {}\r\n'.format(e))
            
    def test(self, tries=10):
        USB0.send('STM32 Library Test START\r\n')
        
        x = 0
        while x < tries:
            res = self.flush_rx_buffer()
            USB0.send('{}\r\n'.format(res))
            
            res = self.send_totx_buffer('01030000000305CB',16)
            USB0.send('{}\r\n'.format(res))
            
            res = self.count_rx_buffer()
            USB0.send('{}\r\n'.format(res))
            
            count = int(res[1])
            res = self.read_rx_buffer(count)
            USB0.send('{}\r\n'.format(res))
                   
            x += 1
            time.sleep(2)
            
        USB0.send('STM32 Library Test STOP\r\n')
        

if __name__ == "__main__":    
    stm = STM32()
    stm.test()

        
    
    
    
