import sqlite3
import json
import os


def db_connection():
  return sqlite3.connect('mvps_data.db')


def get_mvp_data():
  with open('./mvps_data.json', encoding='utf-8') as mvp_data:
    return json.load(mvp_data)


def create_db():
  conn = db_connection()
  cursor = conn.cursor()
  cursor.execute("""
    create table if not exists"mvp" (
      "id" integer not null primary key,
      "name" varchar(50),
      "favorite" integer not null default 0
    );
  """)
  cursor.execute("""
    create table if not exists "respawn" (
      "id" integer not null primary key autoincrement,
      "mvp_id" integer not null,
      "map_id" text not null,
      "time" integer not null
    );
  """)
  cursor.execute("""
    create table if not exists "active" (
      "id" integer not null primary key autoincrement,
      "mvp_id" integer not null,
      "map_id" text not null,
      "time" integer not null
    );
  """)
  conn.commit()
  conn.close()


def populate():
  conn = db_connection()
  cursor = conn.cursor()

  mvp_data = get_mvp_data()
  mvp_list = [] 
  respawn_list = []
  
  for mvp in mvp_data: 
    mvp_list.append((mvp['id'], mvp['name']))
    for map in mvp['maps']:
      respawn_list.append((mvp['id'], map['mapName'], map['respawnTime']))

  cursor.executemany('insert into mvp(id, name) values(?, ?)', mvp_list)
  cursor.executemany('insert into respawn(mvp_id, map_id, time) values(?, ?, ?)', respawn_list)

  conn.commit()
  conn.close()


def show_mvps():
  conn = db_connection()
  cursor = conn.cursor()
  cursor.execute('select * from mvp')
  for linha in cursor.fetchall():
    print(linha) 
  conn.close()


def show_respawn():
  conn = db_connection()
  cursor = conn.cursor()
  cursor.execute('select mvp_id, map_id, time from respawn;')
  for linha in cursor.fetchall():
    print(linha) 
  conn.close()


def init():
  if os.path.exists('./mvps_data.db'):
    os.remove('./mvps_data.db') 
  create_db()
  populate()
  print('MVPs')
  show_mvps()
  print('\nRespawns')
  show_respawn()
