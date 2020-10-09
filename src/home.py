import json
import mimetypes
import re
import threading
from urllib import parse
from time import sleep

import sys
import pychromecast
import requests
import pretty_errors


def die(message, code):
    print(message)
    exit(code)


def error(message):
    print("\033[31m\033[1mError\033[0m: " + message)


def ok():
    print("\033[34mOK.\033[0m")


preCasts = pychromecast.get_chromecasts()
casts = []
nowCast = None
nowId = 0


def run_command(label, args):
    global casts
    global nowCast
    global nowId

    if label == "echo":
        word = " ".join(args)
        print(word)
        return

    if len(args) == 0:
        if label == "exit" or label == "bye" or label == "stop":
            die("Bye.", 0)
        elif label == "list" or label == "device" or label == "devices" or label == "ls":
            for i, cast in enumerate(casts, start=1):
                print_device(i, cast.device)
            return
        elif label == "rc" or label == "reconnect":
            casts = []
            con()
            return
        elif label == "show" or label == "status":
            if nowCast is not None:
                print("Select: [Id=" + str(nowId) + ", Name=" +
                      nowCast.device.friendly_name + ", Model=" +
                      nowCast.device.model_name + "]")
                print("\033[1mStatus\033[0m:")
                print("    Idle: " + str(nowCast.is_idle))
                print("    Volume: " +
                      str("{:.0%}".format(nowCast.status.volume_level)))
                media = nowCast.media_controller
                if media.is_active:
                    print("\033[1m\033[35m♪\033[0m \033[1mPlaying\033[0m:")
                    print("    Current: " + str(media.status.current_time))
                    print("    Media: " + media.status.content_id)
                return
        elif label == "kill":
            if not nowCast.is_idle:
                confirm = input("\033[1mAre you sure?\033[0m (Y/n): ").lower()
                if confirm in "y" or confirm in "\n":
                    print("Killing...")
                    nowCast.quit_app()
                else:
                    print("Cancelled.")
            else:
                error("Device is idling")
            return
    elif len(args) == 1:
        if label == "use" or label == "select":
            name = args[0]
            if name.isdecimal() and len(casts) >= int(name) and name != "0":
                nowCast = casts[int(name) - 1]
                print_device(name, nowCast.device)
                nowId = int(name)
                nowCast.wait()
                return
            for i, cast in enumerate(casts, start=1):
                if cast.device.friendly_name == name:
                    print_device(i, cast.device)
                    nowId = i
                    nowCast = cast
                    nowCast.wait()
                    return
            error("Device not found.")
            print("\033[1mls\033[0m to show device list.")
            return
        elif label == "play" or label == "sound" or label == "music" or label == "p":
            url = args[0]
            if is_url(url):
                mime = mimetypes.guess_type(url)[0]
                if is_youtube(url):
                    video_id = get_youtube_id(url)
                    if video_id is None:
                        error("Failed to parse selected URL.")
                        return
                    yt = get_youtube_file(video_id)
                    if yt is None:
                        return
                    url = yt["url"]
                    mime = yt["mime"]
                media = nowCast.media_controller
                media.play_media(url, mime)
                media.block_until_active()
                print("Playing...")
                return
            error("\033[4m\033[34m" + url + "\033[0m is not url!")
            return
    error("Command not found.")


def con():
    global casts
    if len(preCasts[0]) == 0:
        error("Device not found.")
        return
    if len(preCasts) - 1 > 1:
        print("\033[32mFound\033[0m: \033[1m" + str(len(preCasts) - 1) +
              "\033[0m device found.")
    else:
        print("\033[32mFound\033[0m: \033[1m" + str(len(preCasts) - 1) +
              "\033[0m devices found.")

    for cast in preCasts:
        if str(type(cast)) != "<class 'zeroconf.ServiceBrowser'>" and cast[
                0].device.cast_type == "audio":
            casts += cast
            print_device(len(casts), cast[0].device)


def s_con():
    global casts
    global preCasts
    preCasts = pychromecast.get_chromecasts()
    if len(preCasts[0]) == 0:
        return
    for cast in preCasts:
        if str(type(cast)) != "<class 'zeroconf.ServiceBrowser'>" and cast[
                0].device.cast_type == "audio":
            casts += cast


def command(input_cmd):
    command = input_cmd.split(" ")
    while "" in command:
        command.remove("")
    if len(command) == 0:
        return
    args = command[1:]
    command = command[0]

    run_command(command, args)


def wait_command():
    while True:
        ipt = ""
        try:
            # TODO: Add readline features
            print("\033[1m>\033[0m ", end="")
            ipt = input()
        except EOFError:
            break
        command(ipt)
        print("\033[32mOK.\033[0m")


def print_device(device_id, device):
    print("\033[1mDevice\033[0m: [Id=" + str(device_id) + ", Name=" +
          device.friendly_name + ", Model=" + device.model_name + "]")


def auto_select():
    global nowCast
    if len(casts) == 0:
        return
    nowCast = preCasts[0][0]
    print("\033[1mDevice selected\033[0m:")
    nowCast.wait()


def is_url(url):
    s = re.compile(r"^(http|https|ftp|blob)://")
    if url in " ":
        return False
    return s.match(url)


def is_youtube(url):
    s = re.compile(r"^((https|http)://)?(www\.)?youtu(be|\.be)?(\.com)?")
    return s.match(url)


# Author: https://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python
def get_youtube_id(url):
    query = parse.urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse.parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/' or query.path[:3] == '/v/':
            return query.path.split('/')[2]
    error("Hostname didn't match any hosts")
    return None


def get_youtube_file(youtube_id):
    url = "https://youtube.com/get_video_info?video_id=" + youtube_id + "&asv=3&hl=en"
    resp = requests.get(url)
    if resp.status_code != 200:
        error("Youtube returned status \033[32m" + str(resp.status_code) +
              "\033[0m.")
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

    if "status" in param and param["status"] == "fail":
        error("Youtube response isn't includes \033[1m\033[32mstatus\033[0m")
        return None

    if "player_response" in param:
        player_response = json.loads(param["player_response"])
        return {
            "url": player_response["streamingData"]["formats"][0]["url"],
            "mime": player_response["streamingData"]["formats"][0]["mimeType"]
        }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        del sys.argv[0]
        con()
        auto_select()
        command(" ".join(sys.argv))
        exit(0)

    pretty_errors.configure(separator_character='*',
                            filename_display=pretty_errors.FILENAME_EXTENDED,
                            line_number_first=True,
                            display_link=True,
                            lines_before=5,
                            lines_after=2,
                            line_color=pretty_errors.BRIGHT_RED + '> ' +
                            pretty_errors.default_config.line_color,
                            code_color='  ' +
                            pretty_errors.default_config.line_color,
                            truncate_code=True,
                            display_locals=True)
    pretty_errors.activate()
    print("  \033[1m\033[44mGoogleHome CLI\033[0m")
    print(
        "\033[1mMade-By\033[0m: P2P-Develop [\033[34mGitHub\033[0m: \033[34m\033[4mhttps://github.com/P2P-Develop\033[0m]"
    )
    print(
        "\033[1mContribute in GitHub\033[0m: \033[34m\033[4mhttps://github.com/P2P-Develop/GoogleHomeCLI\033[0m"
    )
    print()
    con()
    try:
        command_thread = threading.Thread(target=wait_command)
        command_thread.daemon = True
        auto_select()
        print("\033[32mReady.\033[0m")
        command_thread.start()
        while True:
            sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print()
        die("Bye.", 0)
