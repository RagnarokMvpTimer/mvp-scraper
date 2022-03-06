from extractor import start as extractor_start
import db


if __name__ == '__main__':
  print('==Extractor==')
  extractor_start()

  print('\n==Database==')
  db.init()
