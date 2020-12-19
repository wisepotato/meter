# Meter

This project reads out your Dutch [DSMR](https://www.netbeheernederland.nl/_upload/Files/Slimme_meter_15_a727fce1f1.pdf) meter and puts it into an InfluxDB.

* Loosely based on [this guide](https://infi.nl/nieuws/hobbyproject-slimme-meterkast-met-raspberry-pi/)

## Development

* Uses python3.8

## Environment Variables

* DB_TYPE (currently only `influxdb` is supported)
* DB_HOSTNAME
* DB_PORT
* DB_USERNAME
* DB_PASSWORD
* DB_DATABASE
* CURRENT_DATA_INTERVAL_SECONDS
* TOTAL_DATA_INTERVAL_SECONDS
