import requests
from lxml import html
import json
import os


def get_mvps_id():
  print('Fetching mvps ids from website...')
  temp = []
  for x in range(1, 3):
    html_src = requests.get(f'https://www.divine-pride.net/database/monster?Flag=4&Page={x}').content
    tree = html.fromstring(html_src)
    mvps_href = tree.xpath('//*[tbody]//*[tr]//*[@class="mvp"]/span/a/@href')
    for href in mvps_href:
      temp.append(href.rsplit('/', 4)[3])
  return temp


def filter_maps(maps):
  print('Filtering maps...')
  temp = []
  for item in maps:
    if item['respawnTime'] != 0:
      temp.append({
        "mapName": item['mapname'],
        "respawnTime": item['respawnTime']
      })
  return temp


def filter_mvp(mvp):
  print('Filtering mvp...')
  return {
    "id": mvp['id'],
    "name": mvp['name'],
    "maps": filter_maps(mvp['spawn'])
  }


def get_mvp_info(mvp_id, api_key):
  print(f'Fetching mvp info id: {mvp_id} ...')
  mvp_info = requests.get(f'https://www.divine-pride.net/api/database/Monster/{mvp_id}?apiKey={api_key}').json()
  return mvp_info


def get_mvp_icon(mvp_id):
  image_path = f'./mvps_icons/{mvp_id}.png'
  if not (os.path.exists(image_path)):
    print(f'Downloading mvp icon {mvp_id}.png ...')
    url = f'https://static.divine-pride.net/images/mobs/png/{mvp_id}.png'
    image_data = requests.get(url).content
    with open(image_path, 'wb') as image:
      image.write(image_data)
      print(f'Saved mvp icon {mvp_id}.png')


def init():
  if not os.path.exists('./mvps_icons/'):
    os.makedirs('./mvps_icons/')

  if not(os.path.exists('./mvps_data.json')):
    api_key = input('Enter your api key\n> ')
    mvps_ids = get_mvps_id()
    mvps_data = []
    for mvp_id in mvps_ids:
      mvp_info = get_mvp_info(mvp_id, api_key)
      if len(mvp_info['spawn']) >= 1 :
        mvps_data.append(filter_mvp(mvp_info))
        get_mvp_icon(mvp_id.rstrip('\n'))

    with open('./mvps_data.json', 'w') as mvps_data_file:
      json.dump(mvps_data, mvps_data_file, indent=2)
