import USB0

import time

import stm32

try:
    import modbus
except Exception as e:
    USB0.send('IMPORT ERROR: {}\r\n'.format(e))


class FIF():
    
    def __init__(self, stm32, usb_log=False):
        try:
            self.__usb_log = usb_log
            self.__stm = stm32
            
        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR __init__(): {}\r\n'.format(e))
        
    def read_LE_0xM(self, addr, meterf):
        '''Function reads LE-0xM meter returning energy consumption in float kWh
        
        :param addr (int): meter address
        
        :return (tuple) (int): [0] -> (1,) for success, (0,) for error
                (tuple) (str): [1] -> ('',) hex response from the meter
                (tuple) (int): [2] -> (x,) decompiled address of the meter
                (tuple) (int): [3] -> (x,) decompiled modbus function
                (tuple) (int): [4] -> (x,) decompiled modbus bytes count
                (tuple) (int): [5] -> (x,) decompiled modbus register 0 value
                (tuple) (int): [6] -> (x,) decompiled modbus register 1 value
                (tuple) (int): [7] -> (x,) decompiled modbus register 2 value
                (tuple) (int): [8] -> (x,) decompiled modbus CRC-16
                (tuple) (int): [9] -> (x.x,) decompiled energy consumption i kWh
        '''
        try:
            self.__stm.flush_rx_buffer()
            
            req = modbus.read_hold_regs(addr,0,3)
            self.__stm.send_totx_buffer(req, 16)
            
            res = self.__stm.count_rx_buffer()
            count = int(res[1])
            
            res = self.__stm.read_rx_buffer(count)
            
            if res[0] != -1 and len(res[2])==22:
                
                res1 = res[2]
                
                res_saddr = int(res1[0:2], 16)
                res_func = int(res1[2:4], 16)
                res_bytec = int(res1[4:6], 16)
                res_r0 = int(res1[6:10], 16)
                res_r1 = int(res1[10:14], 16)
                res_r2 = int(res1[14:18], 16)
                res_crc = int(res1[18:22], 16)
            
                return (1, res[2], res_saddr, res_func, res_bytec, \
                    res_r0, res_r1, res_r2, res_crc, self.__alg(res_r0, res_r1, res_r2, meterf))
           
            else: 
                return (0,)
            
            if self.__usb_log: USB0.send('Read LE0xM: {}\r\n'.format(res))
        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR read_LE_0xM(): {}\r\n'.format(e))
    
    
    def change_addr_LE_0xM(self, addr, new_addr):
        '''Function changes modbus address on LE-0xM meters
        
        :param addr (int): current address
        :param new_addr (int): new address
        
        :return (tuple): (1,) for success, (0,) for error
        '''
        try:
            self.__stm.flush_rx_buffer()
            
            req = modbus.set_single_reg(addr, 7, new_addr)
            self.__stm.send_totx_buffer(req, 16)
            
            res = self.__stm.count_rx_buffer()
            count = int(res[1])
            
            res = self.__stm.read_rx_buffer(count)
            
            if res[2] == req:
                return (1,)
            else:
                return (0,)
            
        except Exception as e:
            if self.__usb_log: USB0.send('FATAL ERROR change_addr_LE_0xM(): {}\r\n'.format(e))
            
            
    def __alg(self, r0, r1, r2, meterf):
        # calculates current consumption form 3 (int) registers
        r0 = float(r0)
        r1 = float(r1)
        r2 = float(r2)
        res = 0.0
        if meterf == 1:
            res = float(((r0*(256**2)+(r1*256)+r2))/100)
        elif meterf == 3:
            res = float(((r0*(256**2)+(r1*256)+r2))/10)
        return res
            

    def test(self, tries=10):
        # test function
        try:
            USB0.send('FIF Library Test START\r\n')
        
            x = 0
            while x < tries:
                res = self.read_LE_0xM(10)
                USB0.send('{}\r\n'.format(res))
                time.sleep(2)
                
                #res = self.change_addr_LE_0xM(x, x+1) # testing from 1 to 10 with pushed SET button
                #USB0.send('{}\r\n'.format(res))
                #time.sleep(2)
                
                x += 1
                
            USB0.send('FIF Library Test STOP\r\n')
        except Exception as e:
            USB0.send('FATAL ERROR WHILE LOOP: {}\r\n'.format(e))
        

if __name__ == "__main__":
    stm4 = stm32.STM32()
    fif = FIF(stm4, usb_log=True)
    fif.test()
    

            
        
    


        
