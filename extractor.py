import json
import os
from typing import Optional

import requests
from lxml import html

from utils import download_img


USE_FILTER = False
NO_ICONS = False
NO_MAP_IMGS = False
IGNORE_EMPTY_MAPS = False
HEADERS = {
  'Accept-Language': 'en-US'
}
STATS_FILTER = ['level', 'health', 'baseExperience', 'jobExperience']


def get_mvp_icon(mvp_id: str) -> None:
  download_img(
    f'./mvps_icons/{mvp_id}.png',
    f'https://static.divine-pride.net/images/mobs/png/{mvp_id}.png',
    'Icon already exists, skipping...',
    f'[{mvp_id}] Downloading mvp icon {mvp_id}.png',
    f'[{mvp_id}] Completed download mvp icon {mvp_id}.png',
    f'[{mvp_id}] Failed to download mvp icon {mvp_id}.png',
  )


def get_map_img(map_name: str, mvp_id: str) -> None:
  download_img(
    f'./maps/{map_name}.png',
    f'https://www.divine-pride.net/img/map/original/{map_name}',
    f'[{mvp_id}] Map img already exists, skipping...',
    f'[{mvp_id}] Downloading map {map_name}.png',
    f'[{mvp_id}] Completed download map {map_name}.png',
    f'[{mvp_id}] Failed to download map {map_name}.png'
  )
  download_img(
    f'./maps/{map_name}_raw.png',
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


def filter_maps(maps: list) -> list[dict]:
  filtered_maps = []
  for item in maps:
    if item['respawnTime'] != 0:
      filtered_maps.append({
        "mapName": item['mapname'],
        "respawnTime": item['respawnTime']
      })
  return filtered_maps


def filter_stats(stats: dict) -> dict:
  filtered_stats = {}
  for item in stats:
    if item in STATS_FILTER:
      filtered_stats[item] = stats[item]
  return filtered_stats


def filter_mvp(mvp: dict) -> dict:
  print(f'[{mvp["id"]}] Filtering mvp...')
  return {
    'id': mvp['id'],
    'dbname': mvp['dbname'],
    'name': mvp['name'],
    'maps': filter_maps(mvp['spawn']),
    'stats': filter_stats(mvp['stats'])
  }


def get_mvp_info(mvp_id: str, api_key: str) -> Optional[dict]:
  print(f'[{mvp_id}] Fetching mvp info...')
  mvp_info = requests.get(
    f'https://www.divine-pride.net/api/database/Monster/{mvp_id}?apiKey={api_key}',
    headers=HEADERS).json()
  return mvp_info if mvp_info else None


def init() -> None:
  try:
    print(f'MVPs will {"not " if not USE_FILTER else ""}be filtered.')
    print(f'MVPs Icons will {"not " if NO_ICONS else ""}be downloaded.')
    print(f'MVPs Maps will {"not " if NO_MAP_IMGS else ""}be downloaded.')

    if not NO_ICONS and not os.path.exists('./mvps_icons/'):
      os.makedirs('./mvps_icons/', exist_ok=True)
    if not NO_MAP_IMGS and not os.path.exists('./maps/'):
      os.makedirs('./maps/', exist_ok=True)
    if os.path.exists('./mvps_data.json'):
      override = input('mvps_data.json already exists, override? (y/n) ')
      if override.lower() == 'n':
        print('Aborting...')
        return

    api_key = input('Enter your divine pride api key\n> ')

    mvps_ids = get_mvps_id()
    if not mvps_ids:
      raise Exception('No mvps ids found.')

    mvps_data = []
    for mvp_id in mvps_ids:
      mvp_info = get_mvp_info(mvp_id, api_key)
      if not mvp_info:
        print(f'[{mvp_id}] Failed to fetch mvp info, skipping...')
        continue
      if IGNORE_EMPTY_MAPS and len(mvp_info['spawn']) == 0:
        print(f'[{mvp_id}] No spawn maps, skipping...')
        continue
      mvps_data.append(mvp_info if not USE_FILTER else filter_mvp(mvp_info))
      if not NO_ICONS:
        get_mvp_icon(mvp_id.rstrip('\n'))
      if not NO_MAP_IMGS:
        for map_i in mvp_info['spawn']:
          get_map_img(map_i['mapname'], mvp_id)
    with open('./mvps_data.json', 'w', encoding='utf-8') as mvps_data_file:
      json.dump(mvps_data, mvps_data_file, indent=2)
  except KeyboardInterrupt:
    print('Aborting...')
  except Exception as e:
    print(f'{e} | {e.__class__.__name__}')


if __name__ == '__main__':
  init()
