from config import TOKEN
import requests
import sqlite3


def send_video_tg(video_path, caption):
    db = sqlite3.connect('data.db')
    cur = db.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                 device_id text,
                  subs_ids text)''')
    db.commit()
    subs = cur.execute("SELECT subs_ids FROM devices WHERE device_id = 'test'").fetchall()
    if len(subs) > 0:
        subs = str(subs[0][0])
        subs = subs.split(', ')
        print(subs)
        video_id = ''
        for index, sub in enumerate(subs):
            if index == 0:
                url = f'https://api.telegram.org/bot{TOKEN}/sendVideo'
                data = {
                    'chat_id': sub,
                    'caption': caption
                }
                files = {'video': open(video_path, 'rb')}
                results = requests.post(url, files=files, data=data)
                print(results)
                results = results.json()
                video_id = str(results["result"]["video"]["file_id"])
            else:
                url = f'https://api.telegram.org/bot{TOKEN}/sendVideo'
                data = {
                    'chat_id': sub,
                    'caption': caption,
                    'video': video_id
                }
                results = requests.post(url, data=data)
                print(results)
    cur.close()
    db.close()


def send_photo_tg(photo_path, caption):
    db = sqlite3.connect('data.db')
    cur = db.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                 device_id text,
                  subs_ids text)''')
    db.commit()
    subs = cur.execute("SELECT subs_ids FROM devices WHERE device_id = 'test'").fetchall()
    if len(subs) > 0:
        subs = str(subs[0][0])
        subs = subs.split(', ')
        print(subs)
        photo_id = ''
        for index, sub in enumerate(subs):
            if index == 0:
                url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto'
                data = {
                    'chat_id': sub,
                    'caption': caption
                }
                files = {'photo': open(photo_path, 'rb')}
                results = requests.post(url, files=files, data=data)
                print(results)
                results = results.json()
                photo_id = str(results["result"]["photo"][2]["file_id"])
            else:
                url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto'
                data = {
                    'chat_id': sub,
                    'caption': caption,
                    'photo': photo_id
                }
                results = requests.post(url, data=data)
                print(results)
    cur.close()
    db.close()


def send_location_tg():
    db = sqlite3.connect('data.db')
    cur = db.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                 device_id text,
                  subs_ids text)''')
    db.commit()
    subs = cur.execute("SELECT subs_ids FROM devices WHERE device_id = 'test'").fetchall()
    if len(subs) > 0:
        subs = str(subs[0][0])
        subs = subs.split(', ')
        print(subs)
        for index, sub in enumerate(subs):
            url = f'https://api.telegram.org/bot{TOKEN}/sendLocation'
            data = {
                'chat_id': sub,
                'latitude': 54.8735,
                'longitude': 69.1491
            }
            results = requests.post(url, data=data)
            print(results)
    db.close()

# send_video_tg('../WIN_20240331_12_39_56_Pro.mp4')
# send_photo_tg('../WIN_20230917_14_16_45_Pro.jpg')