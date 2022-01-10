import json
import os
from typing import Optional

import requests
from lxml import html

from mvp_scraper.utils import download_img


def get_mvp_icon(mvp_id: str) -> None:
  download_img(
    f'./mvps_icons/{mvp_id}.png',
    f'https://static.divine-pride.net/images/mobs/png/{mvp_id}.png',
    f'[{mvp_id}] Icon already exists, skipping...',
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
  return [
    {
      "mapname": item['mapname'],
      "respawnTime": item['respawnTime']
    }
    for item in maps
    if item['respawnTime'] != 0
  ]


def filter_stats(stats: dict, desired_stats: list[str]) -> dict:
  filtered_stats = {}
  for item in stats:
    if item in desired_stats:
      filtered_stats[item] = stats[item]
  return filtered_stats


def filter_mvp(mvp: dict, desired_stats: list[str]) -> dict:
  print(f'[{mvp["id"]}] Filtering mvp...')
  return {
    'id': mvp['id'],
    'dbname': mvp['dbname'],
    'name': mvp['name'],
    'maps': filter_maps(mvp['spawn']),
    'stats': filter_stats(mvp['stats'], desired_stats)
  }


def get_mvp_info(mvp_id: str, api_key: str, headers: Optional[dict] = None) -> Optional[dict]:
  print(f'[{mvp_id}] Fetching mvp info...')
  mvp_info = requests.get(
    f'https://www.divine-pride.net/api/database/Monster/{mvp_id}?apiKey={api_key}',
    headers=headers or {'Accept-Language': 'en-US'}
  ).json()
  return mvp_info if mvp_info else None


def extractor(use_filter: bool = False, no_icons: bool = False, no_map_imgs: bool = False,
              ignore_empty_maps: bool = False,
              desired_stats: Optional[list[str]] = None,
              headers: Optional[dict] = None) -> None:
  try:
    print(f'MVPs will {"not " if not use_filter else ""}be filtered.')
    print(f'MVPs Icons will {"not " if no_icons else ""}be downloaded.')
    print(f'MVPs Maps will {"not " if no_map_imgs else ""}be downloaded.')

    if not no_icons and not os.path.exists('./mvps_icons/'):
      os.makedirs('./mvps_icons/', exist_ok=True)
    if not no_map_imgs and not os.path.exists('./maps/'):
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
      mvp_info = get_mvp_info(mvp_id, api_key, headers)
      if not mvp_info:
        print(f'[{mvp_id}] Failed to fetch mvp info, skipping...')
        continue
      if ignore_empty_maps and not len(mvp_info['spawn']):
        print(f'[{mvp_id}] No spawn maps, skipping...')
        continue

      mvps_data.append(mvp_info if not use_filter else filter_mvp(mvp_info, desired_stats))

      if not no_icons:
        get_mvp_icon(mvp_id.rstrip('\n'))
      if not no_map_imgs:
        for map_i in mvp_info['spawn']:
          get_map_img(map_i['mapname'], mvp_id)

    with open('./mvps_data.json', 'w', encoding='utf-8') as mvps_data_file:
      json.dump(mvps_data, mvps_data_file, indent=2)

  except KeyboardInterrupt:
    print('Aborting...')
  except Exception as e:
    print(f'{e} | {e.__class__.__name__}')


def init():
  no_icons = False
  no_map_imgs = False
  ignore_empty_maps = False
  use_filter = False
  desired_stats = ['level', 'health', 'baseExperience', 'jobExperience']
  headers = None  # {'Accept-Language': 'pt-BR'}

  extractor(use_filter, no_icons, no_map_imgs, ignore_empty_maps, desired_stats, headers)


if __name__ == '__main__':
  init()
