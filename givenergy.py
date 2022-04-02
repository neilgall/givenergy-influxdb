from dataclasses import dataclass
from datetime import datetime
from dateutil.parser import *
import logging
import requests
import time

GIVENERGY_BASE_URL = 'https://api.givenergy.cloud/v1'


@dataclass
class Snapshot:
  inverter: str
  timestamp: str
  battery_percent: int
  solar_power_watts: float
  grid_power_watts: float
  battery_power_watts: float
  consumption_watts: float
  battery_temperature_c: float
  inverter_temperature_c: float


class Givenergy:
  """
  Simple Givenergy API client
  """
  def __init__(
    self,
    api_token: str,
    base_url: str = GIVENERGY_BASE_URL
  ):
    self._base_url = base_url
    self._client = requests.Session()
    self._client.headers.update({
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {api_token}'
    })
    self._inverter = self._discover_inverter()


  def _get(self, url: str):
    for attempt in range(0, 5):
      try:
        rsp = self._client.get(url)
        data = rsp.json()
        rsp.close()
        return data
      except ConnectionAbortedError as e:
        logging.warning(f"failed to GET {url}: {e}")
        time.sleep(1)


  def _discover_inverter(self) -> str:
    """
    Discover the Inverter serial number
    """
    url = f'{self._base_url}/communication-device'
    device_info = self._get(url)
    return device_info['data'][0]['inverter']['serial']


  def get_latest_system_data(self) -> Snapshot:
    """
    Fetch latest system data snapshot
    """
    def _parse_timestamp(t: str) -> str:
      """Parse and normalise timestamp"""
      return parse(t).astimezone().isoformat()

    url = f'{self._base_url}/inverter/{self._inverter}/system-data/latest'
    data = self._get(url)['data']
    return Snapshot(
      # normalise to net zero:
      # - grid power, battery discharge and solar power are positive
      # - consumption and battery charge are negative
      inverter=self._inverter,
      timestamp=_parse_timestamp(data['time']),
      battery_percent=int(data['battery']['percent']),
      solar_power_watts=float(data['solar']['power']),
      grid_power_watts=float(data['grid']['power']) * -1,
      battery_power_watts=float(data['battery']['power']),
      consumption_watts=float(data['consumption']) * -1,
      battery_temperature_c=float(data['battery']['temperature']),
      inverter_temperature_c=float(data['inverter']['temperature'])
    )



if __name__ == "__main__":
  import os
  g = Givenergy(os.environ["GIVENERGY_API_TOKEN"])
  print(g.get_latest_system_data())
