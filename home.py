import pychromecast
import mimetypes
import threading
from urllib import parse
import re
import requests
import json


def die(str):
    print(str)
    exit(1)


preCasts = pychromecast.get_chromecasts()
casts = []
nowCast = None
nowId = 0


def runCommand(label, args):
    global casts
    global nowCast
    global nowId

    if label == "echo":
        word = " ".join(args)
        print(word)
        return

    if len(args) == 0:
        if label == "exit" or label == "bye" or label == "stop":
            die("Bye.")
        elif label == "list" or label == "device" or label == "devices" or label == "ls":
            count = 0
            for cast in casts:
                count += 1
                printDevice(count, cast.device)
            return
        elif label == "rc" or label == "reconnect":
            casts = []
            con()
            return
        elif label == "show" or label == "status":
            if nowCast is not None:
                print("Select: [Id=" + str(nowId) + ", Name=" + nowCast.device.friendly_name + ", Model=" + nowCast.device.model_name + "]")
                print("Status:")
                print("    Idle: " + str(nowCast.is_idle))
                print("    Volume: " + str("{:.0%}".format(nowCast.status.volume_level)))
                media = nowCast.media_controller
                if media.is_active:
                    print("Playing:")
                    print("    Current: " + str(media.status.current_time))
                    print("    Media: " + media.status.content_id)
                return
        elif label == "kill":
            if not nowCast.is_idle:
                confirm = input("Are you sure?(y/n): ")
                if confirm in "y":
                    print("Killing...")
                    nowCast.quit_app()
                else:
                    print("Cancelled.")
            else:
                print("Error: Device is Idling")
            return
    elif len(args) == 1:
        if label == "use" or label == "select":
            name = args[0]
            if name.isdecimal() and len(casts) >= int(name) and name != "0":
                nowCast = casts[int(name) - 1]
                printDevice(name, nowCast.device)
                nowId = int(name)
                nowCast.wait()
                return
            else:
                count = 0
                for c in casts:
                    count += 1
                    if c.device.friendly_name == name:
                        printDevice(count, c.device)
                        nowId = count
                        nowCast = c
                        nowCast.wait()
                        return
                print("Error: Device not found.")
                print("Execute 'ls' to Show Device list.")
                return
        elif label == "play" or label == "sound" or label == "music":
            url = args[0]
            if isUrl(url):
                mime = mimetypes.guess_type(url)[0]
                if isYoutube(url):
                    videoId = getYTid(url)
                    if videoId is None:
                        print("Error: Failed to URL Parsing")
                        return
                    yt = getYTFile(videoId)
                    if yt is None:
                        print("Error: An error has occurred.")

                    url = yt["url"]
                    mime = yt["mime"]
                media = nowCast.media_controller
                media.play_media(url, mime)
                media.block_until_active()
                print("Playing...")
                return
            else:
                print("Error: '" + url + "' is not url!")
                return
    print("Error: Command not found.")


def con():
    global casts
    if len(preCasts[0]) is 0:
        print("Error: ChromeCast not found.")
        return
    print("Found: " + str(len(preCasts) - 1) + " ChromeCast(s) found.")

    for cast in preCasts:
        if str(type(cast)) != "<class 'zeroconf.ServiceBrowser'>" and cast[0].device.cast_type == "audio":
            casts += cast
            printDevice(len(casts), cast[0].device)


def sCon():
    global casts
    global preCasts
    preCasts = pychromecast.get_chromecasts()
    if len(preCasts[0]) is 0:
        return
    for cast in preCasts:
        if str(type(cast)) != "<class 'zeroconf.ServiceBrowser'>" and cast[0].device.cast_type == "audio":
            casts += cast


def command(input):
    command = input.split(" ")
    while "" in command:
        command.remove("")
    if len(command) is 0:
        return
    args = command[1:]
    command = command[0]

    runCommand(command, args)


def waitCommand():
    while True:
        ipt = input(">")
        command(ipt)
        print("OK.")


def printDevice(id, device):
    print("Device: [Id=" + str(id) + ", Name=" + device.friendly_name + ", Model=" + device.model_name + "]")


def autoSelect():
    global nowCast
    if len(casts) == 0:
        return
    nowCast = preCasts[0][0]
    print("Device AutoSelected:")
    nowCast.wait()


def isUrl(url):
    s = re.compile(r"^(http|https|ftp|blob)://")
    if url in " ":
        return False
    return s.match(url)


def isYoutube(url):
    s = re.compile(r"^((https|http)://)?(www\.)?youtu(be|\.be)?(\.com)?")
    return s.match(url)


# Author: https://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python
def getYTid(url):
    query = parse.urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse.parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None


def getYTFile(id):
    url = "https://youtube.com/get_video_info?video_id=" + id + "&asv=3&hl=en"
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Error: An Unknown Error Occurred")
        print(resp.text)
        return None
    r = resp.text.split("&")
    param = {}
    for parm in r:
        lst = parm.split("=")
        if len(lst) != 2:
            continue
        key = lst[0]
        value = parse.unquote(lst[1])
        param[key] = value

    if "status" in param:
        if param["status"] == "fail":
            return None

    if "player_response" in param:
        player_response = json.loads(param["player_response"])
        return {"url": player_response["streamingData"]["formats"][0]["url"], "mime": player_response["streamingData"]["formats"][0]["mimeType"]}


if __name__ == "__main__":
    print("-=-=-=-=[GoogleHome CLI]=-=-=-=-")
    print("Made-By: Peyang")
    print()
    con()
    commandThread = threading.Thread(target=waitCommand)
    autoSelect()
    print("Ready.")
    commandThread.start()
