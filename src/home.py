import json
import mimetypes
import re
import threading
from urllib import parse

import sys
import pychromecast
import requests
import pretty_errors

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import FuzzyCompleter, NestedCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexer import RegexLexer
from pygments.token import *


class CommandLexer(RegexLexer):
    name = "Command"
    aliases = ["cmd"]
    filenames = None

    tokens = {
        'root':
        [(r'^echo', Keyword), (r'^exit', Keyword), (r'^bye', Keyword),
         (r'^stop', Keyword), (r'^list', Keyword), (r'^device', Keyword),
         (r'^devices', Keyword), (r'^ls', Keyword), (r'^reconnect', Keyword),
         (r'^rc', Keyword), (r'^show', Keyword), (r'^status', Keyword),
         (r'^kill', Keyword), (r'^use', Keyword), (r'^select', Keyword),
         (r'^play', Keyword), (r'^sound', Keyword), (r'^music', Keyword),
         (r'^p', Keyword), (r'^#.*$', Comment)]
    }


def die(message, code):
    print(message)
    exit(code)


error = lambda message: print("\033[31m\033[1mError\033[0m: " + message)

ok = lambda: print("\033[34mOK.\033[0m")

preCasts = pychromecast.get_chromecasts()
casts = []
nowCast = None
nowId = 0


def run_command(label, args):
    global casts
    global nowCast
    global nowId

    if label == "echo":
        print(" ".join(args))

        return True

    if len(args) == 0:
        if label == "exit" or label == "bye" or label == "stop":
            print("Bye.")

            return False
        elif label == "list" or label == "device" or label == "devices" or label == "ls":
            for i, cast in enumerate(casts, start=1):
                print_device(i, cast.device)

            return True
        elif label == "rc" or label == "reconnect":
            casts = []
            con()

            return True
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

                return True
        elif label == "kill":
            if not nowCast.is_idle:
                confirm = input("\033[1mAre you sure?\033[0m (Y/n): ").lower()

                if confirm in "y" or confirm in "\n":
                    print("Killing...")
                    nowCast.quit_app()
                else:
                    print("Cancelled.")

            else:
                error("Device is idling.")

            return True
    elif len(args) == 1:
        if label == "use" or label == "select":
            name = args[0]

            if name.isdecimal() and len(casts) >= int(name) and name != "0":
                nowCast = casts[int(name) - 1]
                print_device(name, nowCast.device)
                nowId = int(name)
                nowCast.wait()

                return True

            for i, cast in enumerate(casts, start=1):
                if cast.device.friendly_name == name:
                    print_device(i, cast.device)
                    nowId = i
                    nowCast = cast
                    nowCast.wait()

                    return True

            error("Device not found.")
            print("\033[1mls\033[0m to show device list.")

            return True
        elif label == "play" or label == "sound" or label == "music" or label == "p":
            url = args[0]

            if is_url(url):
                mime = mimetypes.guess_type(url)[0]

                if is_youtube(url):
                    video_id = get_youtube_id(url)

                    if video_id is None:
                        error("Failed to parse selected URL.")

                        return True

                    yt = get_youtube_file(video_id)

                    if yt is None:
                        return True

                    url = yt["url"]
                    mime = yt["mime"]

                media = nowCast.media_controller
                media.play_media(url, mime)
                media.block_until_active()
                print("Playing...")

                return True

            error("\033[4m\033[34m" + url + "\033[0m is not url!")

            return True

    error("Command not found.")

    return True


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

    casts += [
        cast for cast in preCasts
        if str(type(cast)) != "<class 'zeroconf.ServiceBrowser'>"
        and cast[0].device.cast_type == "audio"
    ]


def command(input_cmd):
    if input_cmd.startswith("#"):
        return True

    command = input_cmd.split(" ")

    while "" in command:
        command.remove("")

    if len(command) == 0:
        return True

    return run_command(command[0], command[1:])


def wait_command():
    session = PromptSession()
    while True:
        ipt = ""

        try:
            ipt = session.prompt("> ",
                                 completer=FuzzyCompleter(
                                     NestedCompleter.from_nested_dict({
                                         "echo":
                                         None,
                                         "exit":
                                         None,
                                         "bye":
                                         None,
                                         "stop":
                                         None,
                                         "list":
                                         None,
                                         "device":
                                         None,
                                         "devices":
                                         None,
                                         "ls":
                                         None,
                                         "kill":
                                         None,
                                         "status":
                                         None,
                                         "show":
                                         None,
                                         "reconnect":
                                         None,
                                         "rc":
                                         None,
                                         "use":
                                         None,
                                         "select":
                                         None,
                                         "play": {
                                             "youtu.be/": None,
                                             "./": None,
                                             "/": None
                                         },
                                         "p": {
                                             "youtu.be/": None,
                                             "./": None,
                                             "/": None
                                         }
                                     })),
                                 auto_suggest=AutoSuggestFromHistory(),
                                 lexer=PygmentsLexer(CommandLexer))
        except KeyboardInterrupt:
            print("Bye.")
            break

        if not command(ipt):
            break

        ok()


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
    if url in " ":
        return False
    return re.compile(r"^(http|https|ftp|blob)://").match(url)


is_youtube = lambda url: re.compile(
    r"^((https|http)://)?(www\.)?youtu(be|\.be)?(\.com)?").match(url)


# Author: https://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python
def get_youtube_id(url):
    query = parse.urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return parse.parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/' or query.path[:3] == '/v/':
            return query.path.split('/')[2]
    error("Hostname didn't match any hosts")
    return None


def get_youtube_file(youtube_id):
    resp = requests.get("https://youtube.com/get_video_info?video_id=" +
                        youtube_id + "&asv=3&hl=en")

    if resp.status_code != 200:
        error("Youtube returned status \033[32m" + str(resp.status_code) +
              "\033[0m")
        print(resp.text)
        return None

    param = {}

    for parm in resp.text.split("&"):
        lst = parm.split("=")

        if len(lst) != 2:
            continue

        param[lst[0]] = parse.unquote(lst[1])

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
        "\033[1mMade by\033[0m: P2P-Develop [\033[34mGitHub\033[0m: \033[34m\033[4mhttps://github.com/P2P-Develop\033[0m]"
    )
    print(
        "\033[1mContribute in GitHub\033[0m: \033[34m\033[4mhttps://github.com/P2P-Develop/GoogleHomeCLI\033[0m"
    )
    print()
    con()
    try:
        command_thread = threading.Thread(target=wait_command)
        command_thread.setDaemon(True)
        auto_select()
        print("\033[32mReady.\033[0m")
        command_thread.start()
        command_thread.join()
    except KeyboardInterrupt:
        print()
        die("Bye.", 0)
