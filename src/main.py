import re
import serial
from statistics import mean
from datetime import datetime
from typing import List
from dotenv import load_dotenv
import contextlib
from dataclasses import dataclass


load_dotenv()

# Settings
import os
database_type = os.getenv("DB_TYPE")
database_host = os.getenv("DB_HOSTNAME")
database_port = int(os.getenv("DB_PORT"))
database_username = os.getenv("DB_USERNAME")
database_password = os.getenv("DB_PASSWORD")
database_database = os.getenv("DB_DATABASE")

allowed_database_types = ['influxdb']

if database_type not in allowed_database_types:
    raise Exception(f"The database_type {database_type} is not allowed. Allowed types: {allowed_database_types}")

from influxdb import InfluxDBClient

client = InfluxDBClient(
    host=database_host,
    port=database_port,
    username=database_username,
    password=database_password,
    database=database_database
)

class InfluxImporter:
    client: InfluxDBClient

    def __init__(self, client: InfluxDBClient):
        self.client = client

    
current_wattages = []

def process_reading(watt_current: float, watt_total_low: float, watt_total_high: float, total_gas: float) -> None:
  global current_wattages
  current_date = datetime.now().isoformat()
  current_wattages.append(watt_current)
  if len(current_wattages) == 10:
    # done with a minute, lets write
    avg = mean(current_wattages)
    json_body = [
      {
          "measurement": "energy",
          "time": current_date,
          "fields": {
              "current_electricity_kw": float(avg),
              "total_electricity_low_kwh": watt_total_low,
              "total_electricity_high_kwh": watt_total_high,
              "total_gas_m3": total_gas,
          }
      }
    ]
    current_wattages = []
    client.write_points(json_body)

class DmsrFourTelegram:
    current_usage_electricity: float
    total_usage_electricity_low: float
    total_usage_electricity_high: float

@dataclass
class DsmrInfo:
    variable_name: str
    search_for: str
    unit: str


class DsmrFour():
    _serial : serial.Serial
    lines: List[str] = []
    ending_character: str = "!"

    _registrations: List[DsmrInfo] = []
    def __init__(self, ser: serial.Serial):
        ser.baudrate = 115200
        ser.bytesize = serial.EIGHTBITS
        ser.parity = serial.PARITY_NONE
        ser.stopbits = serial.STOPBITS_ONE
        ser.xonxoff = 0
        ser.rtscts = 0
        ser.timeout = 12
        ser.port = "/dev/ttyUSB0"
        self._serial = ser
    
    def register(self,data_unit: DsmrInfo)  -> None:
        self._registrations.append(data_unit)

    def interpret(self, lines: List[str]) -> List:
        data = []
        for finder in self._registrations:
            for text in lines:
                if finder.search_for in text:
                    groups = re.findall(rf'([0-9]+[\.]+[0-9]*\*{finder.unit})',text)

                    text = [group.replace(f"*{finder.unit}", "") for group in groups if str(group).endswith(f"*{finder.unit}")][0]
                    actual_float = float(text)
                    data.append({
                        'variable_name' : finder.variable_name,
                        'value' : actual_float,
                        'unit' : finder.unit
                    })
        return data

    def get_lines(self) -> List[str]:
        return self.lines

    def print_lines(self) -> None:
        for line in self.lines:
            print(line)

    def end_of_telegram(self, line: str) -> bool:
        return self.ending_character in line


    def wait_for_telegram_and_load(self) -> None:
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


dsmr = DsmrFour(serial.Serial())
data_units = [
    DsmrInfo(variable_name="total_gas", search_for="0-1:24.2.1", unit="m3"),
    DsmrInfo(variable_name="current_electricity", search_for="1-0:1.7.0",  unit="kW"),
    DsmrInfo(variable_name="total_electricity_high", search_for="1-0:1.8.1", unit="kWh"),
    DsmrInfo(variable_name="total_electricity_low", search_for="1-0:1.8.2", unit="kWh"),
]

for du in data_units:
    dsmr.register(du)

def get_reading(data: List, name: str):
    return list(filter(lambda x: x["variable_name"] == name, data))[0]["value"]

#def process_reading(watt_current: float, watt_total_low: float, watt_total_high: float, total_gas: float) -> None:
while True:
    dsmr.wait_for_telegram_and_load()
    lines = dsmr.get_lines()
    interpreted = dsmr.interpret(lines)
    print(interpreted)
    process_reading(
            watt_current=get_reading(interpreted, "current_electricity"),
            watt_total_low=get_reading(interpreted, "total_electricity_low"),
            watt_total_high=get_reading(interpreted, "total_electricity_high"),
            total_gas=get_reading(interpreted, "total_gas")
            )
