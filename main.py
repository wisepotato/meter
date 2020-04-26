import re
import serial
from statistics import mean
from datetime import datetime
from typing import List

import contextlib



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


class DmsrFourTelegram:
    current_usage_electricity: float
    total_usage_electricity_low: float
    total_usage_electricity_high: float

class DsmrInfo:

    def __init__(self, variable: str, search_for: str,  unit: str):
        self.variable_name = variable
        self.search_for = search_for
        self.unit = unit
    variable_name: str
    search_for: str
    unit: str

class DsmrFour():
    _serial : serial.Serial
    lines: List[str] = []

    _registrations: List[DsmrInfo] = []
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
    
    def register(self,data_unit: DsmrInfo)  -> None:
        self._registrations.append(data_unit)

    def interpret(self) -> None:
        for finder in self._registrations:
            for text in self.lines:
                if finder.search_for in text:
                    groups = re.findall(r'\((.*?)\)',text)

                    text = [group.replace(f"*{finder.unit}", "") for group in groups if str(group).endswith(f"*{finder.unit}")][0]
                    actual_float = float(text)
                    print(f"{finder.variable_name} - {actual_float} {finder.unit}")

    def print_lines(self) -> None:
        for line in self.lines:
            print(line)

    def end_of_telegram(self, line: str) -> bool:
        return re.match('(?=!)', line)


    @contextlib.contextmanager
    def start(self) -> 'DsmrFour':
        self._serial.open()
        self.lines = []
        while  True:
            telegram_line = self._serial.readline()
            telegram_line = telegram_line.decode('ascii').strip()
            if self.end_of_telegram(telegram_line):
                break
            else:
                self.lines.append(telegram_line)

        self._serial.close()
        yield self


dsmr = DsmrFour(serial.Serial())
data_units = [
    DsmrInfo(variable="total_gas", search_for="0-1:24.2.1", unit="m3"),
    DsmrInfo(variable="current_electricity", search_for="1-0:1.7.0",  unit="kW"),
    DsmrInfo(variable="total_electricity_high", search_for="1-0:1.8.1", unit="kWh"),
    DsmrInfo(variable="total_electricity_low", search_for="1-0:1.8.2",unit="kWh"),
]

for du in data_units:
    dsmr.register(du)

while True:
    with dsmr.start() as dsmr:
        dsmr.interpret()
    


    
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