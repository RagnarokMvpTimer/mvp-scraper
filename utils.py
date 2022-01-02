import os

import requests


def download_img(output_path: str, url: str, on_exist: str, on_start: str, on_complete: str, on_error: str) -> None:
  if os.path.exists(output_path):
    return print(on_exist)

  print(on_start)
  data = requests.get(url).content

  if len(data) <= 0:
    #raise Exception('')
    return print(on_error)

  with open(output_path, 'wb') as file:
    file.write(data)
    print(on_complete)
