import json
import multiprocessing as mp
import os
from pathlib import Path
from typing import Optional

import requests
from environs import Env
from lxml import html

from mvp_scraper.utils import download_img, get_output_path


def get_mvp_icon(mvp_id: str, output_path: Path) -> None:
  download_img(
    output_path.joinpath('mvps_icons', f'{mvp_id}.png'),
    f'https://static.divine-pride.net/images/mobs/png/{mvp_id}.png',
    f'[{mvp_id}] Icon already exists, skipping...',
    f'[{mvp_id}] Downloading mvp icon {mvp_id}.png',
    f'[{mvp_id}] Completed download mvp icon {mvp_id}.png',
    f'[{mvp_id}] Failed to download mvp icon {mvp_id}.png',
  )


def get_map_img(map_name: str, mvp_id: str, output_path: Path) -> None:
  download_img(
    output_path.joinpath('maps', f'{map_name}.png'),
    f'https://www.divine-pride.net/img/map/original/{map_name}',
    f'[{mvp_id}] Map img already exists, skipping...',
    f'[{mvp_id}] Downloading map {map_name}.png',
    f'[{mvp_id}] Completed download map {map_name}.png',
    f'[{mvp_id}] Failed to download map {map_name}.png'
  )
  download_img(
    output_path.joinpath('maps', f'{map_name}_raw.png'),
    f'https://www.divine-pride.net/img/map/raw/{map_name}',
    f'[{mvp_id}] Raw Map img already exists, skipping...',
    f'[{mvp_id}] Downloading raw map {map_name}.png',
    f'[{mvp_id}] Completed download raw map {map_name}.png',
    f'[{mvp_id}] Failed to download raw map {map_name}.png'
  )


def get_mvps_id() -> list[str]:
  print('Fetching mvps ids from divine pride...')
  ids = []
  for i in range(1, 2):
    html_src = requests.get(f'https://www.divine-pride.net/database/monster?Flag=4&Page={i}').content
    tree = html.fromstring(html_src)
    mvps_href = tree.xpath('//*[tbody]//*[tr]//*[@class="mvp"]/span/a/@href')
    for href in mvps_href:
      ids.append(href.rsplit('/', 4)[3])
  print(f'Found {len(ids)} mvps ids.')
  return ids


class Filter:
  def __init__(self, desired_stats: Optional[list[str]] = None) -> None:
    self.desired_stats = desired_stats

  @staticmethod
  def filter_maps(maps: list) -> list[dict]:
    return [
      {
        "mapname": item['mapname'],
        "respawnTime": item['respawnTime']
      }
      for item in maps
      if item['respawnTime'] != 0
    ]

  def filter_stats(self, stats: dict) -> dict:
    return stats if not self.desired_stats else \
      {
        item: stats[item]
        for item in stats
        if item in self.desired_stats
      }

  def filter_mvp(self, mvp: dict) -> dict:
    print(f'[{mvp["id"]}] Filtering mvp...')
    return {
      'id': mvp['id'],
      'dbname': mvp['dbname'],
      'name': mvp['name'],
      'spawn': self.filter_maps(mvp['spawn']),
      'stats': self.filter_stats(mvp['stats'])
    }


class Extractor:
  def __init__(self,
               use_filter: bool = False,
               no_icons: bool = False,
               no_map_images: bool = False,
               ignore_mvp_with_empty_maps: bool = False,
               desired_stats: Optional[list[str]] = None,
               api_key: str = None,
               headers: Optional[dict] = None,
               output_path: Optional[Path] = None
               ) -> None:
    self.use_filter = use_filter
    self.no_icons = no_icons
    self.no_map_images = no_map_images
    self.ignore_mvp_with_empty_maps = ignore_mvp_with_empty_maps
    self.desired_stats = desired_stats
    self.api_key = api_key
    self.headers = headers or {'Accept-Language': 'en-US'}
    self.filter = Filter(desired_stats)
    self.output_path = output_path or get_output_path()

  def get_mvp_info(self, mvp_id: str) -> Optional[dict]:
    print(f'[{mvp_id}] Fetching mvp info...')
    mvp_info = requests.get(
      f'https://www.divine-pride.net/api/database/Monster/{mvp_id}?apiKey={self.api_key}',
      headers=self.headers
    ).json()
    return mvp_info if mvp_info else None

  def get_mvp_data(self, mvp_id: str) -> Optional[dict]:
    mvp_info = self.get_mvp_info(mvp_id)

    if not mvp_info:
      return print(f'[{mvp_id}] Failed to fetch mvp info, skipping...')

    if self.use_filter:
      mvp_info = self.filter.filter_mvp(mvp_info)

    if self.ignore_mvp_with_empty_maps and not len(mvp_info['spawn']):
      return print(f'[{mvp_id}] No spawn maps, skipping...')

    if not self.no_icons:
      get_mvp_icon(mvp_id.rstrip('\n'), self.output_path)

    if not self.no_map_images:
      for map_item in mvp_info['spawn']:
        get_map_img(map_item['mapname'], mvp_id, self.output_path)

    return mvp_info

  def extract(self) -> None:
    try:
      print(f'MVPs will {"not " if not self.use_filter else ""}be filtered.')
      print(f'MVPs Icons will {"not " if self.no_icons else ""}be downloaded.')
      print(f'MVPs Maps will {"not " if self.no_map_images else ""}be downloaded.')

      if not self.no_icons and not self.output_path.joinpath('mvps_icons').exists():
        Path.mkdir(self.output_path.joinpath('mvps_icons'), parents=True, exist_ok=True)

      if not self.no_map_images and not self.output_path.joinpath('maps').exists():
        Path.mkdir(self.output_path.joinpath('maps'), parents=True, exist_ok=True)

      if self.output_path.joinpath('mvps_data.json').exists():
        override = input('mvps_data.json already exists, override? (y/n) ')
        if override.lower() == 'n':
          return print('Aborting...')

      mvps_ids = get_mvps_id()
      if not mvps_ids:
        raise Exception('No mvps ids found.')

      pool = mp.Pool(os.cpu_count() or 1)
      mvps_data = pool.starmap(self.get_mvp_data, zip(mvps_ids))
      mvps_data = list(filter(lambda item: item is not None, mvps_data))

      with self.output_path.joinpath('mvps_data.json').open('w', encoding='utf-8') as mvps_data_file:
        json.dump(mvps_data, mvps_data_file, indent=2)

    except KeyboardInterrupt:
      print('Aborting...')
    except Exception as e:
      # print(f'{e} | {e.__class__.__name__}')
      exit()


def start() -> None:
  env = Env()
  env.read_env()

  divine_pride_api_key = env.str('DIVINE_PRIDE_API_KEY', None)
  if not divine_pride_api_key:
    return print('Divine pride api not found, aborting...')

  no_icons = env.bool('NO_ICONS', False)
  no_map_images = env.bool('NO_MAP_IMAGES', False)
  ignore_mvp_with_empty_maps = env.bool('IGNORE_MVP_WITH_EMPTY_MAPS', False)
  use_filter = env.bool('USE_FILTER', False)
  desired_stats = env.list('DESIRED_STATS', None)
  output_path = get_output_path()

  extractor = Extractor(use_filter, no_icons, no_map_images, ignore_mvp_with_empty_maps, desired_stats,
                        divine_pride_api_key,
                        output_path=output_path)
  extractor.extract()


if __name__ == '__main__':
  start()
