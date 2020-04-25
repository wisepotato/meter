import re
import serial
 
# Seriele poort confguratie
ser = serial.Serial()
 
# DSMR 2.2 > 9600 7E1:
# ser.baudrate = 9600
# ser.bytesize = serial.SEVENBITS
# ser.parity = serial.PARITY_EVEN
# ser.stopbits = serial.STOPBITS_ONE
 
# DSMR 4.0/4.2 > 115200 8N1:
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
 
ser.xonxoff = 0
ser.rtscts = 0
ser.timeout = 12
ser.port = "/dev/ttyUSB0"
ser.close()
 

from influxdb import InfluxDBClient

from datetime import datetime

client = InfluxDBClient()

from statistics import mean

current_wattages = []

def add_wattage(watt_current: float, watt_total_low: float, watt_total_high: float) -> None:
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
              "watt_current": float(avg),
              "watt_total_low": watt_total_low,
              "watt_total_low": watt_total_high
          }
      }
    ]
    current_wattages = []
    client.write_points(json_body)



while True:
  ser.open()
  checksum_found = False
  
  current_wattage = 0.0
  while not checksum_found:
    
    telegram_line = ser.readline() # Lees een seriele lijn in.
    telegram_line = telegram_line.decode('ascii').strip() # Strip spaties en blanke regels
    if re.match(str('(?=1-0:1.7.0)'), str(telegram_line)): #1-0:1.7.0 = Actueel verbruik in kW
      # 1-0:1.7.0(0000.54*kW)
      kw = telegram_line[10:-4] # Knip het kW gedeelte eruit (0000.54)
      watt = float(kw) * 1000 # vermengvuldig met 1000 voor conversie naar Watt (540.0)
      watt = int(watt) # rond float af naar heel getal (540)\
      current_wattage = watt


    
  
 
    # Check wanneer het uitroepteken ontvangen wordt (einde telegram)
    if re.match('(?=!)', telegram_line):
      checksum_found = True
      add_wattage(watt)
 
  ser.close()
