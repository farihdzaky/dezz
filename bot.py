from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters
from pydeezer import Deezer
import re
import requests
import os
import asyncio
import deezer as deez
from deezloader.deezloader import DeeLogin
from deezloader.deezloader.dee_api import API
from pydub import AudioSegment
from io import BytesIO
from asyncio import Queue
from concurrent.futures import ThreadPoolExecutor

arl = "dab723e90f58ec5a992c635559db633e42cba072e66359cf085034079e6ab29e28c96a2f0fcf099b7e47816a305adb69717a2ff85dd079137d9bc432a46842412435f80ebf906a1f7c6880729ad5f3e2166f2fc997fcdc3876585a45d4109042"
deezer = Deezer()
user_info = deezer.login_via_arl(arl)

dez = deez.Client(app_id='662971', app_secret='cd1f27edcb7f2115804df2fe6418a41b')
downloa = DeeLogin(
            arl='636788036a88607ab002681a884808947c031c76830158c15511be10384425de1190764668abb0a53aa22b79b6db67ae79cf3641751a85ae7b20c095188638a340290bd0ec23801b80fc2295b7b882ad97a0ddb89af6642b1e7726c8a8d4dac3',
            email='farihmuhammad75@gmail.com',
            password='farih2009',
)

#track_search_results = deezer.search_tracks("Who Am I - alan walker")
#print(track_search_results[0]['id'])
api = API()
# Extract track ID from the link
download_status = {}
# Get the track
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}
# Download directory
download_dir = r'./musik'

# Telegram setup

api_id = '2374504'
api_hash = '2ea965cd0674f1663ec291313edcd333'
bot_token = '6719685688:AAFDBfUN-meUgkk1jCTZTluLdkxmp38I0eE'

# Create the client and connect to Telegram
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def convert_mp3_to_flac(mp3_path):
    audio = AudioSegment.from_file(mp3_path, format="mp3")
    flac_io = BytesIO()
    audio.export(flac_io, format="flac")
    flac_bytes = flac_io.getvalue()
    return flac_bytes

is_downloading = False

@app.on_message(filters.command(["start"]))
async def start(client, message):
    #global is_downloading
    #if is_downloading:
        #await client.send_message(message.chat.id, "Bot is currently downloading another music from other user. Please wait.")
        #return
    #else:
       await message.reply_text('Welcome! Please choose an option:', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Deezer", callback_data="deezer")]]))

@app.on_callback_query(filters.create(lambda _, __, query: query.data == "deezer"))
async def deezer_option(client, callback_query):
    await callback_query.message.reply_text('Please send the Deezer link.')

@app.on_message(filters.text)
async def process_deezer_link(client, message):
   # global is_downloading
   # if is_downloading:
       # await client.send_animation(message.chat.id, "Bot is currently downloading another songs. Please wait.")
       # return
    #else:
    response = requests.get(message.text)
    final_url = response.url
    clean_url = re.sub(r'www\.|\?.*$', '', final_url)
    track_id = re.findall(r'\d+', clean_url)[-1]
    
    if 'deezer.com/en/track/' in final_url:
        track = dez.get_track(track_id)
        # Prepare the caption
        caption = f"🎵 Song Name: {track.title}\n"
        caption += f"🎤 Artist: {track.artist}\n"
        caption += f"⏱ Duration: {track.duration}\n"
        caption += f"📝 Release date: {track.release_date}\n"
        caption += f"👥 Contributor: {track.contributors}\n"
        caption += f"🎵 Track Position: {track.track_position}"

        # Prepare the buttons
        buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Download FLAC', callback_data=f"flac.{clean_url}")],
         [InlineKeyboardButton(text='Download MP3', callback_data=f"mp3.{clean_url}")]
     ])
        
        await app.send_message(message.chat.id, caption, reply_markup=buttons)

    elif 'deezer.com/en/playlist' in final_url:
        playlist = dez.get_playlist(track_id)
        playlist_media = playlist.picture_medium
        # Prepare the caption
        caption = f"🎧 Playlist Name: {playlist.title}\n"
        caption += f"👤 Owner: {playlist.creator}\n"
        caption += f"👥 Number of tracks: {playlist.nb_tracks}\n"
        caption += f"⏱ Duration: {playlist.duration}\n"
        buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Download FLAC', callback_data=f"flacpl.{clean_url}")],
         [InlineKeyboardButton(text='Download MP3', callback_data=f"mp3pl.{clean_url}")]
     ])
        
        await app.send_photo(message.chat.id, playlist_media, caption=caption, reply_markup=buttons)

    elif 'deezer.com/en/album' in final_url:
        album = dez.get_album(track_id)
        album_media = album.cover_medium
        # Prepare the caption
        caption = f"📀 Album Name: {album.title}\n"
        caption += f"👤 Artist: {album.artist}\n"
        caption += f"👥 Number of tracks: {album.nb_tracks}\n"
        caption += f"⏱ Duration: {album.duration}\n"
        buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Download FLAC', callback_data=f"flacal.{clean_url}")],
         [InlineKeyboardButton(text='Download MP3', callback_data=f"mp3al.{clean_url}")]
     ])
        
        await app.send_photo(message.chat.id,album_media, caption=caption, reply_markup=buttons)
    elif 'youtube.com/watch' in final_url:
        


@app.on_message(filters.sticker | filters.audio | filters.photo | filters.animation)
async def invalid_message(client, message):
        await app.send_message(message.chat.id, 'Give me a link or a song name to search!')

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("flacpl")))
async def download_flac_playlist(_, callback_query):
    await app.send_message(callback_query.message.chat.id, "Downloading FLAC playlist...")
    track_parts = callback_query.data.split(".")
    playlist_url = ".".join(track_parts[1:])
    playlist_id = int(playlist_url.split('/')[-1])
    playlist_tracks = deezer.get_playlist_tracks(playlist_id)
    tasks = []
    executor = ThreadPoolExecutor()

    def download_song(track):
        api = track['SNG_ID']
        url = f"https://deezer.com/en/track/{api}"
        # run the blocking download function in the executor
        down = downloa.download_trackdee(url, output_dir='./musik', quality_download='FLAC', recursive_download=True, recursive_quality=True, not_interface=True, method_save=2)
        print(down.song_path)
        return down.song_path
    with ThreadPoolExecutor() as executor:
        for track in playlist_tracks:
            # Schedule download_song to run in the executor
            flac_path, name = await asyncio.get_event_loop().run_in_executor(executor, download_song, track)
            task = asyncio.create_task(app.send_audio(callback_query.message.chat.id, str(flac_path), name))
            tasks.append(task)

    # Wait for all tasks to complete
    await asyncio.gather(*tasks)
    executor.shutdown(wait=True)

# Don't forget to close the executor when done

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("flacal")))
async def download_flac_playlist(_, callback_query):
    await app.send_message(callback_query.message.chat.id, "Downloading Your FLAC Album...")
    track_parts = callback_query.data.split(".")
    playlist_url = ".".join(track_parts[1:])
    playlist_id = int(playlist_url.split('/')[-1])
    playlist_tracks = deezer.get_album_tracks(playlist_id)
    tasks = []
    executor = ThreadPoolExecutor()

    def download_song(track):
        api = track['SNG_ID']
        url = f"https://deezer.com/en/track/{api}"
        # run the blocking download function in the executor
        down = downloa.download_trackdee(url, output_dir='./musik', quality_download='FLAC', recursive_download=True, recursive_quality=True, not_interface=True, method_save=2)
        print(down.song_path)
        return down.song_path
    with ThreadPoolExecutor() as executor:
        for track in playlist_tracks:
            # Schedule download_song to run in the executor
            flac_path, name = await asyncio.get_event_loop().run_in_executor(executor, download_song, track)
            task = asyncio.create_task(app.send_audio(callback_query.message.chat.id, str(flac_path), name))
            tasks.append(task)

    # Wait for all tasks to complete
    await asyncio.gather(*tasks)
    executor.shutdown(wait=True)
# ...

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("mp3pl")))
async def download_flac_playlist(_, callback_query):
    await app.send_message(callback_query.message.chat.id, "Downloading MP3 playlist...")
    track_parts = callback_query.data.split(".")
    playlist_url = ".".join(track_parts[1:])
    playlist_id = int(playlist_url.split('/')[-1])
    playlist_tracks = deezer.get_playlist_tracks(playlist_id)
    tasks = []
    executor = ThreadPoolExecutor()

    def download_song(track):
        api = track['SNG_ID']
        name = track['SNG_TITLE']
        url = f"https://deezer.com/en/track/{api}"
        # run the blocking download function in the executor
        down = downloa.download_trackdee(url, output_dir='./musik', quality_download='MP3_128', recursive_download=True, recursive_quality=True, not_interface=True, method_save=2)
        print(down.song_path)
        return down.song_path
    with ThreadPoolExecutor() as executor:
        for track in playlist_tracks:
            # Schedule download_song to run in the executor
            flac_path, name = await asyncio.get_event_loop().run_in_executor(executor, download_song, track)
            task = asyncio.create_task(app.send_audio(callback_query.message.chat.id, str(flac_path), name))
            tasks.append(task)

    # Wait for all tasks to complete
    await asyncio.gather(*tasks)
    executor.shutdown(wait=True)

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("mp3al")))
async def download_flac_playlist(_, callback_query):
    await app.send_message(callback_query.message.chat.id, "Downloading FLAC playlist...")
    track_parts = callback_query.data.split(".")
    playlist_url = ".".join(track_parts[1:])
    playlist_id = int(playlist_url.split('/')[-1])
    playlist_tracks = deezer.get_playlist_tracks(playlist_id)
    tasks = []
    executor = ThreadPoolExecutor()

    def download_song(track):
        api = track['SNG_ID']
        name = track['SNG_TITLE']
        url = f"https://deezer.com/en/track/{api}"
        # run the blocking download function in the executor
        down = downloa.download_trackdee(url, output_dir='./musik', quality_download='MP3_128', recursive_download=True, recursive_quality=True, not_interface=True, method_save=2)
        print(down.song_path)
        return down.song_path, name
    with ThreadPoolExecutor() as executor:
        for track in playlist_tracks:
            # Schedule download_song to run in the executor
            flac_path, name = await asyncio.get_event_loop().run_in_executor(executor, download_song, track)
            task = asyncio.create_task(app.send_audio(callback_query.message.chat.id, str(flac_path), name))
            tasks.append(task)

    # Wait for all tasks to complete
    await asyncio.gather(*tasks)
    executor.shutdown(wait=True)

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("flac")))
async def download_flac(client, callback_query):
    await app.send_message(callback_query.message.chat.id, "Downloading FLAC...")
    track_parts = callback_query.data.split(".")
    track_url = ".".join(track_parts[1:])  # Join all parts except the first one
    executor = ThreadPoolExecutor()

    with ThreadPoolExecutor() as executor:
        track = await asyncio.get_event_loop().run_in_executor(
            executor, 
            downloa.download_trackdee(
            track_url, 
            '/musik', 
            'FLAC',
            True, 
            False, 
            True,
            2)
        )

    flac_file = f"{track.song_name}.flac"  # Set the name attribute to the track title
    await client.send_audio(callback_query.message.chat.id, audio=flac_file)
    os.remove(track.song_path, flac_file)

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("mp3")))
async def download_mp3(client, callback_query):
    track_parts = callback_query.data.split(".")
    track_url = ".".join(track_parts[1:])  
    executor = ThreadPoolExecutor()

    with ThreadPoolExecutor() as executor:
        track = await asyncio.get_event_loop().run_in_executor(
            executor, 
            downloa.download_trackdee(
            track_url, 
            '/musik', 
            'MP3_320',
            True, 
            False, 
            True,
            2)
        )

    await client.send_audio(callback_query.message.chat.id, audio=track.song_path)
    os.remove(track.song_path)

app.run()