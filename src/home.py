import json
import mimetypes
import os
import re
import sys
import threading
from datetime import datetime
from urllib import parse

import pretty_errors
import pychromecast
import requests
import yaml
from action_completer import ActionCompleter
from gtts import gTTS
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import FuzzyCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexer import RegexLexer, inherit
from pygments.token import *


class BaseLexer(RegexLexer):
    tokens = {
        'root': [
            (r'^(//|#|"|;|/\*.*?\*/).*$', Comment),
            (r'"', String, 'string'),
            (r'\'', String, 'string'),
            (r'`', String, 'string'),
            (r'\s+', Text),
        ],
        'string': [
            (r'[^"]+', String),
            (r'[^\']+', String),
            (r'[^`]+', String),
            (r'"|\'|`', String, '#pop'),
        ]
    }


class CommandLexer(BaseLexer):
    name = "Command"
    aliases = ["cmd"]
    filenames = None

    tokens = {
        'root': [
            (r'^echo', Keyword),
            (r'^exit', Keyword),
            (r'^bye', Keyword),
            (r'^stop', Keyword),
            (r'^list', Keyword),
            (r'^devices?', Keyword),
            (r'^ls', Keyword),
            (r'^reconnect', Keyword),
            (r'^rc', Keyword),
            (r'^show', Keyword),
            (r'^status', Keyword),
            (r'^kill', Keyword),
            (r'^use', Keyword),
            (r'^select', Keyword),
            (r'^play', Keyword),
            (r'^sound', Keyword),
            (r'^music', Keyword),
            (r'^p', Keyword),
            (r'^speech', Keyword),
            (r'^speak', Keyword),
            (r'^talk', Keyword),
            (r'^tts', Keyword),
            (r'[0-9]+', Number),
            inherit,
        ],
        'string': [
            (r'[^"\\]+', String),
            (r'[^\'\\]+', String),
            (r'[^`\\]+', String),
            (r'\\.', String.Escape),
            (r'"|\'|`', String, "#pop"),
        ]
    }


def die(message: str, code: int) -> None:
    print(message)
    exit(code)


def error(message: str) -> None:
    print("\033[31m\033[1mError\033[0m: " + message)


def ok() -> None:
    print("\033[34mOK.\033[0m")


preCasts = pychromecast.get_chromecasts()
casts = []
cmd_completer: ActionCompleter = ActionCompleter()
nowCast = None
nowId = 0
prefix = "> "


@cmd_completer.action("echo",
                      capture_all=True,
                      display_meta="Prints characters to the console")
@cmd_completer.param(None)
def _echo_action(*args) -> None:
    if " ".join(args) == "":
        print()
        return

    if " ".join(args).replace("\\\"", "").count("\"") % 2 != 0 or \
        " ".join(args).count("'") % 2 != 0 or \
        " ".join(args).count("`") % 2 != 0:
        error("Quotes are not closed.")

        return

    print(" ".join(args).replace("\\r", "").replace("\\n", "\n").replace(
        "\"", "").replace("\\", "\"").replace("'", "").replace("`", ""))


@cmd_completer.action("exit", display_meta="Exit this script")
@cmd_completer.action("bye", display_meta="Exit this script")
@cmd_completer.action("stop", display_meta="Exit the script")
def _exit_action() -> None:
    die("\033[32mBye.\033[0m", 0)


@cmd_completer.action("speak",
                      display_meta="Play Text-To-Speech from selected device",
                      active=Condition(lambda: nowCast is not None))
@cmd_completer.action("speech",
                      display_meta="Play Text-To-Speech from selected device",
                      active=Condition(lambda: nowCast is not None))
@cmd_completer.action("talk",
                      display_meta="Play Text-To-Speech from selected device",
                      active=Condition(lambda: nowCast is not None))
@cmd_completer.action("tts",
                      display_meta="Play Text-To-Speech from selected device",
                      active=Condition(lambda: nowCast is not None))
@cmd_completer.param(None)
def _tts_action(*args) -> None:
    global nowCast

    if " ".join(args).replace("\\\"", "").count("\"") % 2 != 0 or \
        " ".join(args).count("'") % 2 != 0 or \
        " ".join(args).count("`") % 2 != 0:
        error("Quotes are not closed.")

        return

    if nowCast is not None:
        text = " ".join(args).replace("\"", "").replace("\\", "\"").replace(
            "'", "").replace("`", "")

        tts = gTTS(text=text)

        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

        tts.save(f"cache/{filename}")

        media = nowCast.media_controller

        media.play_media(f"cache/{filename}", "audio/mp3")
        media.block_until_active()

        return

    error("Device isn't selected!")


@cmd_completer.action("list", display_meta="Show recognized devices")
@cmd_completer.action("device", display_meta="Show recognized devices")
@cmd_completer.action("devices", display_meta="Show recognized devices")
@cmd_completer.action("ls", display_meta="Show recognized devices")
def _list_action() -> None:
    global casts

    for i, cast in enumerate(casts, start=1):
        print_device(i, cast.device)


@cmd_completer.action("reconnect", display_meta="Recognize devices again")
@cmd_completer.action("rc", display_meta="Recognize devices again")
def _reconnect_action() -> None:
    global casts

    casts = []

    con()


@cmd_completer.action("show", display_meta="Show connected devices status")
@cmd_completer.action("status", display_meta="Show connected devices status")
def _status_action() -> None:
    global nowCast

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


@cmd_completer.action("kill", display_meta="Kill the selected device", active=Condition(lambda: nowCast is not None))
def _kill_action() -> None:
    if not nowCast.is_idle:
        confirm = input("\033[1mAre you sure?\033[0m (Y/n): ").lower()

        if confirm in "y" or confirm in "\n" or confirm in "true":
            print("Killing...")
            nowCast.quit_app()
        else:
            print("Cancelled.")
    else:
        error("Device is idling.")


@cmd_completer.action("use", display_meta="Select a device in id/name")
@cmd_completer.action("select", display_meta="Select a device in id/name")
@cmd_completer.param([cast.friendly_name for cast in casts],
                     display_meta="Select device \"{completion}\"")
def _use_action(name: str) -> None:
    global casts
    global nowCast
    global nowId

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


@cmd_completer.action(
    "play",
    display_meta="Play URL/local music or video file from the selected device",
    active=Condition(lambda: nowCast is not None))
@cmd_completer.action(
    "sound",
    display_meta="Play URL/local music or video file from the selected device",
    active=Condition(lambda: nowCast is not None))
@cmd_completer.action(
    "music",
    display_meta="Play URL/local music or video file from the selected device",
    active=Condition(lambda: nowCast is not None))
@cmd_completer.action(
    "p",
    display_meta="Play URL/local music or video file from the selected device",
    active=Condition(lambda: nowCast is not None))
@cmd_completer.param(None)
def _play_action(url: str) -> None:
    global nowCast

    if nowCast is None:
        error("Device isn't selected!")

        return

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


def con() -> bool:
    global casts

    if len(preCasts[0]) == 0:
        error("Device not found.")
        return False

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

    return True


def s_con() -> None:
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


def wait_command() -> None:
    global cmd_completer
    global prefix

    session = PromptSession()
    while True:
        ipt = ""

        try:
            ipt = session.prompt(prefix,
                                 completer=FuzzyCompleter(cmd_completer),
                                 auto_suggest=AutoSuggestFromHistory(),
                                 lexer=PygmentsLexer(CommandLexer),
                                 complete_in_thread=True,
                                 mouse_support=True)
        except KeyboardInterrupt:
            print("\033[32mBye.\033[0m")
            break

        if ipt.startswith("#") or ipt.startswith("//") or ipt.startswith(
            "\"") or ipt.startswith(";"):
            ok()
            continue
        elif ipt.startswith("/*"):
            if not ipt.endswith("*/"):
                error("This comment block must be enclosed in */")
                continue
            ok()
            continue

        try:
            cmd_completer.run_action(ipt)
        except ValueError:
            error("Command not found.")
            continue

        ok()


def print_device(device_id: int, device) -> None:
    print("\033[1mDevice\033[0m: [Id=" + str(device_id) + ", Name=" +
          device.friendly_name + ", Model=" + device.model_name + "]")


def auto_select() -> None:
    global nowCast

    if len(casts) == 0:
        return

    nowCast = preCasts[0][0]

    print("\033[1mDevice selected\033[0m:")
    nowCast.wait()


def is_url(url: str):
    if url in " ":
        return False
    return re.compile(r"^(http|https|ftp|blob)://").match(url)


def is_youtube(url: str):
    re.compile(r"^((https|http)://)?(www\.)?youtu(be|\.be)?(\.com)?").match(
        url)


# Author: https://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python
def get_youtube_id(url: str):
    query = parse.urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return parse.parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/' or query.path[:3] == '/v/':
            return query.path.split('/')[2]
    error("Hostname didn't match any hosts")
    return


def get_youtube_file(youtube_id: str):
    resp = requests.get(
        f"https://youtube.com/get_video_info?video_id={youtube_id}&asv=3&hl=en"
    )

    if resp.status_code != 200:
        error(
            f"Youtube returned status \033[32m{str(resp.status_code)}\033[0m")
        print(resp.text)
        return None

    param = {}

    for parm in resp.text.split("&"):
        lst = parm.split("=")

        if len(lst) != 2:
            continue

        param[lst[0]] = parse.unquote(lst[1])

    if "status" in param and param["status"] == "fail":
        error("Youtube response isn't includes \033[1m\033[32emstatus\033[0m")
        return None

    if "player_response" in param:
        player_response = json.loads(param["player_response"])
        return {
            "url": player_response["streamingData"]["formats"][0]["url"],
            "mime": player_response["streamingData"]["formats"][0]["mimeType"]
        }


if __name__ == "__main__":
    try:
        with open(f"{os.path.dirname(__file__)}/config.yml", 'r') as file:
            config = yaml.load(file, Loader=yaml.SafeLoader)
            if config is not None and "prompt" in config:
                prefix = f"{config['prompt']} "
    except FileNotFoundError:
        error("Config file not found.")
    if len(sys.argv) > 1:
        del sys.argv[0]

        if not con():
            exit(1)

        auto_select()
        cmd_completer.run_action(" ".join(sys.argv))
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
    command_thread = threading.Thread(target=wait_command)
    command_thread.setDaemon(True)
    auto_select()
    print("\033[32mReady.\033[0m")
    command_thread.start()
    command_thread.join()
