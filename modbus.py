import USB0
import time

from binascii import hexlify
from binascii import unhexlify

__INITIAL_MODBUS = 0xFFFF
__INITIAL_DF1 = 0x0000

__table = (
0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040 )

def __calcByte( ch, crc):
    """Given a new Byte and previous CRC, Calc a new CRC-16"""
    if type(ch) == type("c"):
        by = ord( ch)
    else:
        by = ch
    crc = (crc >> 8) ^ __table[(crc ^ by) & 0xFF]
    return (crc & 0xFFFF)

def __calcString( st, crc):
    """Given a binary string and starting CRC, Calc a final CRC-16 """
    for ch in st:
        crc = (crc >> 8) ^ __table[(crc ^ ord(ch)) & 0xFF]
    return crc

def __ReverseByteOrder(data):
    """
    Method to reverse the byte order of a given unsigned data value
    Input:
        data:   data value whose byte order needs to be swap
                data can only be as big as 4 bytes
    Output:
        revD: data value with its byte order reversed
    """
    s = "Error: Only 'unsigned' data of type 'int' or 'long' is allowed"
    if not ((type(data) == int)or(type(data) == long)):
        s1 = "Error: Invalid data type: %s" % type(data)
        print(''.join([s,'\n',s1]))
        return data
    if(data < 0):
        s2 = "Error: Data is signed. Value is less than 0"
        print(''.join([s,'\n',s2]))
        return data

    seq = ["0x"]

    while(data > 0):
        d = data & 0xFF     # extract the least significant(LS) byte
        seq.append('%02x'%d)    # convert to appropriate string, append to sequence
        data >>= 8          # push next higher byte to LS position

    revD = int(''.join(seq),16)

    return revD

def read_hold_regs(addr, start, quantity):

    var = []
    var.append(hex(addr)[2:])
    var.append(hex(3)[2:]) # Function 03 (0x03) Read Holding Registers

    if start and quantity < 256:
        var.append('00'+hex(start)[2:])
        var.append('00'+hex(quantity)[2:])
    else:
        var.append('00'+hex(start)[2:]) # TODO sprawdzic dlaczego dodawane sa zera dla warosci od 256. Czy adres moze miec wieksza wartosc?
        var.append('00'+hex(quantity)[2:])

    i = 0
    for ch in var:
        if (len(ch) % 2) != 0:
            x = '0'
            y = ch
            var[i] = x + ch
            if i==2 or i==3:
                x = ''
        i += 1

    hexs = var[0] + var[1] + var[2] + var[3]

    return __get_req_w_crc(unhexlify(hexs))

def set_single_reg(addr, reg, value):

    var = []
    var.append(hex(addr)[2:])
    var.append(hex(6)[2:]) # Function 06 (0x06) Set Single Register

    if value and reg < 256:
        var.append('00'+hex(reg-1)[2:])
        var.append('00'+hex(value)[2:])
    else:
        var.append('00'+hex(reg-1)[2:])
        var.append('00'+hex(value)[2:])

    i = 0
    for ch in var:
        if (len(ch) % 2) != 0:
            x = '0'
            y = ch
            var[i] = x + ch
            if i==2 or i==3:
                x = ''
        i += 1

    hexs = var[0] + var[1] + var[2] + var[3]

    return __get_req_w_crc(unhexlify(hexs))
        

def __get_req_w_crc(hexstr):

    crc = __INITIAL_MODBUS
    for ch in hexstr:
        crc = __calcByte(ch, crc)

    val = hex(__ReverseByteOrder(crc))
    x = val.find('0x')
    y = val[x+2:]

    if (len(y) % 2) != 0:
        x = '0'
        x += y

        res = hexlify(hexstr) + x
        if len(x) < 3:
            res = res + '00'
            return res.upper()
        else: return res.upper()

    else:
        res = hexlify(hexstr) + y
        if len(y) < 3:
            res = res + '00'
            return res.upper()
        else: return res.upper()
        
if __name__ == '__main__':
    USB0.send('modbus Library Test START\r\n')
    i = 1
    while i < 246:
        try:
            USB0.send('Read holding registers from addr: {} - {}\r\n'.format(i, read_hold_regs(i, 0, 3)))
            USB0.send('Set Register 6 for 186 at addr: {} - {}\r\n'.format(i, set_single_reg(i, 7, 186)))
        except Exception as e:
            USB0.send('FATAL ERROR: {}\r\n'.format(e))
        i += 1
    USB0.send('modbus Library Test STOP\r\n')
        

        


