from pydeezer import Deezer
import requests
import re
import json

arl = "dab723e90f58ec5a992c635559db633e42cba072e66359cf085034079e6ab29e28c96a2f0fcf099b7e47816a305adb69717a2ff85dd079137d9bc432a46842412435f80ebf906a1f7c6880729ad5f3e2166f2fc997fcdc3876585a45d4109042"
deezer = Deezer()
user_info = deezer.login_via_arl(arl)

response = requests.get('https://deezer.page.link/Z7SNTNy7P3faRfGy7')
final_url = response.url
clean_url = re.sub(r'www\.|\?.*$', '', final_url)
track_id = re.findall(r'\d+', clean_url)[-1]
tracks = deezer.get_playlist_tracks(track_id)

for track in tracks:
    if track['_POSITION'] > 30:
        print("Can't get track from 50!")
        break
    elif track['_POSITION'] < 30:
        print(track)  # print the track data in JSON format