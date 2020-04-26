import re
import serial
from statistics import mean
from datetime import datetime
from typing import List




# client = InfluxDBClient()


# current_wattages = []

# def add_wattage(watt_current: float, watt_total_low: float, watt_total_high: float) -> None:
#   global current_wattages
#   current_date = datetime.now().isoformat()
#   current_wattages.append(watt_current)
#   if len(current_wattages) == 10:
#     # done with a minute, lets write
#     avg = mean(current_wattages)
#     json_body = [
#       {
#           "measurement": "energy",
#           "time": current_date,
#           "fields": {
#               "watt_current": float(avg),
#               "watt_total_low": watt_total_low,
#               "watt_total_low": watt_total_high
#           }
#       }
#     ]
#     current_wattages = []
#     client.write_points(json_body)

class DsmrFour():
    _serial : serial.Serial
    _lines: List[str] = []


    


    def __init__(self, ser: serial.Serial):
        ser.baudrate = 115200
        ser.bytesize =serial.EIGHTBITS
        ser.parity = serial.PARITY_NONE
        ser.stopbits = serial.STOPBITS_ONE
        ser.xonxoff = 0
        ser.rtscts = 0
        ser.timeout = 12
                
        ser.port = "/dev/ttyUSB0"
        self._serial = ser
    
    def print_lines(self) -> None:
        for line in self._lines:
            print(line)
    def append_line(self, line: str) -> None:
        self._lines.append(line)

    def get_serial(self) -> serial.Serial:
        return self._serial

class SerialContainer(object):
    _lines: List[str] = []
    _serial: serial.Serial

    def __init__(self, dsmr: DsmrFour):
        self._serial = dsmr.get_serial()
        self._dsmr = dsmr

    def __enter__(self) -> 'SerialContainer':
        self._serial.open()
        
        while  True:
            telegram_line = ser.readline()
            telegram_line = telegram_line.decode('ascii').strip()
            if self.end_of_telegram(telegram_line):
                break
            else:
                self._dsmr.append_line(telegram_line)

        return self

    def end_of_telegram(self, line: str) -> bool:
        return re.match('(?=!)', line)

    def __exit__(self, type, value, traceback):
        self._serial.close()



ser = serial.Serial()
dsmr = DsmrFour(ser)

while True:

    with SerialContainer(dsmr)  as sc:
        sc._dsmr.print_lines()



    
    # checksum_found = False
    
    # current_wattage = 0.0
    # while not checksum_found:
        
    #     telegram_line = ser.readline() # Lees een seriele lijn in.
    #     telegram_line = telegram_line.decode('ascii').strip() # Strip spaties en blanke regels
    #     if re.match(str('(?=1-0:1.7.0)'), str(telegram_line)): #1-0:1.7.0 = Actueel verbruik in kW
    #     # 1-0:1.7.0(0000.54*kW)
    #     kw = telegram_line[10:-4] # Knip het kW gedeelte eruit (0000.54)
    #     watt = float(kw) * 1000 # vermengvuldig met 1000 voor conversie naar Watt (540.0)
    #     watt = int(watt) # rond float af naar heel getal (540)\
    #     current_wattage = watt