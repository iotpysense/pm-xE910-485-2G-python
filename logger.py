import utils

def log(info):
    f = open('event.log','a+')
    f.write('{} - {}\r\n'.format(utils.get_TIME(), info))
    f.close()