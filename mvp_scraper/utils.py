import os
from pathlib import Path

import requests
from environs import Env


def get_root_path() -> Path:
  """
  Return project root path.
  :return: PurePath subclass
  """
  return Path(__file__).parent.parent


def get_output_path() -> Path:
  env = Env()
  env.read_env()
  output_path = env.path('OUTPUT_PATH', './output/')

  if not output_path.is_absolute():
    output_path = get_root_path().joinpath(output_path)

  return Path(os.path.normcase(output_path)).resolve()


def download_img(output_path: Path, url: str, on_exist: str, on_start: str, on_complete: str, on_error: str) -> None:
  if Path.exists(output_path):
    return print(on_exist)

  print(on_start)
  data = requests.get(url).content

  if len(data) <= 0:
    # raise Exception('')
    return print(on_error)

  with output_path.open('wb') as image:
    image.write(data)
    print(on_complete)
