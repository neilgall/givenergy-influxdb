from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from givenergy import Givenergy, Snapshot
import argparse
import os
import time


class Updater:
  def __init__(self, args):
    self._influx = InfluxDBClient(
      url=args.influx,
      token=args.influx_token,
      org=args.org
    )
    self._bucket = args.bucket
    self._givenergy = Givenergy(args.givenergy_token)
    self._update_period = args.period


  def run(self):
    with self._influx as client:
      write_api = client.write_api(SYNCHRONOUS)

      try:
        while True:
          self.update(write_api)
          time.sleep(self._update_period)
      
      except KeyboardInterrupt:
        pass
      
      finally:
        client.close()


  def update(self, write_api):
    try:
      snapshot = self._givenergy.get_latest_system_data()
      write_api.write(
        bucket='solar',
        record=snapshot,
        record_measurement_name='snapshot',
        record_tag_keys=['inverter'],
        record_time_key='timestamp',
        record_field_keys=[
          'solar_power_watts',
          'grid_power_watts',
          'battery_power_watts',
          'consumption_watts',
          'battery_percent',
          'battery_temperature_c',
          'inverter_temperature_c'
        ]
      )
      print(f'{snapshot.timestamp} '
        f'solar {snapshot.solar_power_watts} '
        f'grid {snapshot.grid_power_watts} '
        f'battery {snapshot.battery_power_watts} '
        f'consumption {snapshot.consumption_watts} '
    )
    except Exception as e:
      print(f'update failed: {e}')
      

if __name__ == "__main__":
  default_influx_url = os.environ.get('INFLUX_URL', 'http://localhost:8086')
  default_influx_token = os.environ.get('INFLUX_TOKEN')
  default_givenergy_token = os.environ.get('GIVENERGY_API_TOKEN')

  parser = argparse.ArgumentParser()
  parser.add_argument('--influx', default=default_influx_url)
  parser.add_argument('--influx-token', default=default_influx_token)
  parser.add_argument('--org', default='Home')
  parser.add_argument('--bucket', default='solar')
  parser.add_argument('--givenergy-token', default=default_givenergy_token)
  parser.add_argument('--period', type=int, default=300)
  args = parser.parse_args()

  time.sleep(10)

  print(f"updating {args.influx} with period {args.period}")
  Updater(args).run()
