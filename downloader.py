from art import *
from youtubesearchpython import *
from pytube import YouTube
from progress.bar import Bar
import asyncio
import requests
import json
import base64
from moviepy.editor import *
import os
import sys
from mp3_tagger import MP3File, VERSION_BOTH

path = os.path.abspath("pl-downloader")
client_id = ""
client_secret = ""

async def get_playlist(id):
    auth = client_id + ":" + client_secret
    message_bytes = auth.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_string = base64_bytes.decode("ascii") 
    x = requests.post("https://accounts.spotify.com/api/token", data={"grant_type": "client_credentials"}, headers={"Authorization": "Basic {}".format(base64_string)})
    response_data = json.loads(x.text)
    token = response_data.get('access_token')
    x = requests.get("https://api.spotify.com/v1/playlists/{}/tracks".format(id), headers={"Authorization": "Bearer {}".format(token)})
    response_data = json.loads(x.text)
    songs = response_data.get("items")
    canzoni = []
    for i in range(0, len(songs)):
        artista = ""
        canzone = songs[i]["track"]["name"]
        if len(songs[i]["track"]["artists"]) > 1:
            for j in range(0, len(songs[i]["track"]["artists"])):
                if j == 0:
                    artista = songs[i]["track"]["artists"][j]["name"] + " feat "
                elif j==1:
                    artista = artista + songs[i]["track"]["artists"][j]["name"]
                else:
                    artista = artista + ", " +songs[i]["track"]["artists"][j]["name"] + " "
        else:
            artista = songs[i]["track"]["artists"][0]["name"]
        canzoni.append(canzone + " - " + artista)
    return(canzoni)

async def scarica(input):
    titolo = input
    try:
        allSearch = VideosSearch(titolo, limit = 2)
    except:
        return
    diz = []
    diz = allSearch.result(mode = ResultMode.dict)
    link = diz["result"][1]["link"]
    test = await download(link)
    video = VideoFileClip(os.path.join(test))
    try:
        os.mkdir(os.path.join(path,"audio"))
    except:
        pass
    try:
        video.audio.write_audiofile(os.path.join(path,"audio",input + ".mp3"), verbose=False, logger=None)
    except:
        return
    return os.path.join(path,"audio",input + ".mp3")


async def download(link):
    return YouTube(link).streams.filter().first().download(path)
    

async def main():
    if len(sys.argv) != 2:
        id = input("Playlist url: ")
    else:
        id = sys.argv[1]
    id = id.split("/")
    id = id[-1].split("?")[0]
    canzoni = await get_playlist(id)
    giuste = 0
    with Bar('Scarico...', max = len(canzoni)) as bar:
        for canzone in canzoni:
            path = await scarica(canzone)
            if path:
                mp3 = MP3File(path)
                try:
                    mp3.artist = canzone.split("-")[-1][:24]
                except:
                    mp3.artist = canzone.split("-")[-1]
                mp3.save()
            giuste += 1
            bar.next()
    bar.finish()
    print("DONE! I just downloaded ", giuste, " songs!")
    

asyncio.run(main())
