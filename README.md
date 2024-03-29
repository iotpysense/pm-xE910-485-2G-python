# pm-xE910-485-2G-python
Python SW for pm-xE910-485-2G-0x modems

# AT++ Commands:

SW implements custom AT++ commands available at USB0 interface:

- <strong>AT++</strong>
Returns OK if AT++ interpreter runs
- <strong>AT++CONFIG?</strong>
Returns modem configuration.
- <strong>AT++METACH=x,y</strong>
Changes meter modbus address at 'x' address for 'y' address. For example AT++METACH=1,5 changes meter with address 1 for address 5.
- <strong>AT++METTR=x[,y...]</strong>
Sets meters address for readings. For example AT++METTR=1,2,3,4,5 will set up readings from 1,2,3,4,5 modbus addresses.
- <strong>AT++METTEST=x</strong>
Tests meters connection and read out. For example AT++METTEST=1 will test meter with address 1.
- <strong>AT++METERF=x,y,z,k,l</strong>
Sets phase number for the meter. For example AT++METTEST=3,1,3,1,1 will set that 1st and 3rd meter are 3-phase and the rest is 1-phase. It's mandatory for correct power consumption calculation.
- <strong>AT++READTM=x</strong>
Rets reading timeout. For example AT++READTM=300 will set up readings period for 300s (15min).
- <strong>AT++MQTT=CONNECT</strong>
Test procedure for MQTT connection.
- <strong>AT++MQTT=DISCONNECT</strong>
Test procedure for MQTT disconnection.
- <strong>AT++STM=stm_command</strong>
Direct access for STM32 AT commands. For example AT++STM=AT+RS485? sends AT+RS485? command to STM32 at USIF0 interface and returns RS485 configuration.
- <strong>AT++MODEM=gsm_command</strong>
Direct access for Telit modem AT commands. For example AT++MODEM=AT+CPIN? sends AT+CPIN? command to Telit Modem at MDM python interface and returns +CPIN status.
- <strong>AT++QUIT</strong>
Exits from Python program to Telit modem stack.
