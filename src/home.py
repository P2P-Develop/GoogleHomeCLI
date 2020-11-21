import json
import mimetypes
import os
from decimal import Decimal, ROUND_HALF_UP
import re
import sys
import threading
import time
from datetime import datetime
from urllib import parse
from colorama import init, Fore, Back, Style

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
from pygments.lexer import RegexLexer, include
import pygments.token as token


class CommandLexer(RegexLexer):
    name = "Command"
    aliases = ["cmd"]
    filenames = None

    tokens = {
        'root': [
            include('basic'),
            include('data'),
            include('math'),
            include('string')
        ],
        'basic': [
            (r'\b(echo|exit|bye|stop|list|devices?|ls|reconnect|'
             r'rc|show|status|kill|use|select|play|sound|music|'
             r'p|speech|speak|talk|tts)(?=[\s)`])?', token.Name.Builtin),
            (r'\\[\w\W\"\'\`]', token.String.Escape),
            (r'^(//|#|"|;|/\*.*?\*/).*$', token.Comment.Single)
        ],
        'data': [
            (r'\|', token.Punctuation),
            (r'\s+', token.Text),
            (r'\d+\b', token.Number)
        ],
        'math': [
            (r'[-+*/%^|&]|\*\*|\|\|', token.Operator),
            (r'\d+#\d+', token.Number),
            (r'\d+#(?! )', token.Number),
            (r'\d+', token.Number)
        ],
        'string': [
            (r'(?s)\$"(\\\\|\\[0-7]+|\\.|[^"\\])*"', token.String.Double),
            (r'(?s)".*?"', token.String.Double),
            (r"(?s)\$'(\\\\|\\[0-7]+|\\.|[^'\\])*'", token.String.Single),
            (r"(?s)'.*?'", token.String.Single),
            (r"(?s)\$`(\\\\|\\[0-7]+|\\.|[^`\\])*`", token.String.Backtick),
            (r"(?s)`.*?`", token.String.Backtick)
        ]
    }


def die(message: str, code: int) -> None:
    print(message)
    exit(code)


def error(message: str) -> None:
    print(f"{Back.LIGHTRED_EX + Fore.BLACK}  ERROR  {Back.RESET + Fore.LIGHTWHITE_EX} " + message)


def ok(execution_time: float) -> None:
    print(f"{Back.LIGHTGREEN_EX + Fore.BLACK}  OK  {Back.RESET + Fore.LIGHTWHITE_EX} "
          f"The command finished in {Decimal(str(execution_time)).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)}ms.")


def quote_check(args: str) -> bool:
    return " ".join(args).replace("\\\"", "").count("\"") % 2 != 0 or \
           " ".join(args).count("'") % 2 != 0 or \
           " ".join(args).count("`") % 2 != 0


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

    if quote_check(" ".join(args)):
        error("Quotes are not closed.")

        return

    text = " ".join(args).replace("\\r", "").replace("\\n", "\n").replace(
        "\"", "").replace("\\", "\"").replace("'", "").replace("`", "")

    if "|" in text:
        pipes = text.split("|")
        for pipe in pipes[1:]:
            cmd_completer.run_action(f"{pipe} {' '.join(pipes[0].split(' ')[0:])}")
    else:
        print(text)


@cmd_completer.action("exit", display_meta="Exit this script")
@cmd_completer.action("bye", display_meta="Exit this script")
@cmd_completer.action("stop", display_meta="Exit the script")
def _exit_action() -> None:
    die(f"{Fore.LIGHTGREEN_EX}Bye.", 0)


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

    if quote_check(" ".join(args)):
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
        print(f"{Back.LIGHTBLUE_EX + Fore.BLACK}  SUMMARY  {Back.RESET + Fore.LIGHTWHITE_EX} Selected device summary:")
        print(f"    {Fore.GREEN}Id{Fore.RESET}: {Fore.LIGHTCYAN_EX + str(nowId) + Fore.WHITE + Style.DIM},")
        print(f"    {Fore.GREEN}Name{Fore.RESET}: {Fore.LIGHTCYAN_EX + nowCast.device.friendly_name + Fore.WHITE + Style.DIM},")
        print(f"    {Fore.GREEN}Model{Fore.RESET}: {Fore.LIGHTCYAN_EX + nowCast.device.model_name}")
        print()
        print(f"{Back.LIGHTBLUE_EX + Fore.BLACK}  STATUS  {Back.RESET + Fore.LIGHTWHITE_EX} Selected device status:")
        print(f"    {Fore.GREEN}Idle{Fore.RESET}: {Fore.LIGHTCYAN_EX + str(nowCast.is_idle) + Fore.WHITE + Style.DIM},")
        print(f"    {Fore.GREEN}Volume{Fore.RESET}: {Fore.LIGHTCYAN_EX + str('{:.0%}'.format(nowCast.status.volume_level)) + Fore.WHITE + Style.DIM}")

        media = nowCast.media_controller

        if media.is_active:
            print(f"{Back.LIGHTMAGENTA_EX + Fore.BLACK}  PLAYING  {Back.RESET + Fore.LIGHTWHITE_EX} Playing music:")
            print(f"    {Fore.GREEN}Current{Fore.RESET}: {Fore.LIGHTCYAN_EX + str(media.status.current_time) + Fore.WHITE + Style.DIM},")
            print(f"    {Fore.GREEN}Media{Fore.RESET}: {Fore.LIGHTCYAN_EX + media.status.content_id + Fore.WHITE + Style.DIM}")


@cmd_completer.action("kill", display_meta="Kill the selected device", active=Condition(lambda: nowCast is not None))
def _kill_action() -> None:
    if not nowCast.is_idle:
        confirm = input(f"{Fore.BLUE}? {Fore.LIGHTWHITE_EX}Are you sure? {Fore.WHITE + Style.DIM}(Y/n){Style.RESET_ALL} ").lower()

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

        print_device(int(name), nowCast.device)

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
    print(f"{Fore.LIGHTGREEN_EX}ls{Fore.LIGHTWHITE_EX} to show found device list.")


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

    error(f"\033[4m{Fore.LIGHTBLUE_EX + url + Style.RESET_ALL} is not a valid url!")

    return


def con() -> bool:
    global casts

    if len(preCasts[0]) == 0:
        error("Device not found.")
        return False

    if len(preCasts) - 1 > 1:
        print(f"{Back.LIGHTGREEN_EX + Fore.BLACK}  SUCCESS  {Back.RESET} "
              f"{Fore.LIGHTCYAN_EX + str(len(preCasts) - 1) + Fore.RESET} device found.")
    else:
        print(f"{Back.LIGHTGREEN_EX + Fore.BLACK}  SUCCESS  {Back.RESET} "
              f"{Fore.LIGHTCYAN_EX + str(len(preCasts) - 1) + Fore.RESET} devices found.")

    for cast in preCasts:
        if str(type(cast)) != "<class 'zeroconf.ServiceBrowser'>" and cast[0].device.cast_type == "audio":
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
        if str(type(cast)) != "<class 'zeroconf.ServiceBrowser'>" and cast[0].device.cast_type == "audio"
    ]


def wait_command() -> None:
    global cmd_completer
    global prefix

    session = PromptSession()

    while True:
        try:
            ipt = session.prompt(prefix,
                                 completer=FuzzyCompleter(cmd_completer),
                                 auto_suggest=AutoSuggestFromHistory(),
                                 lexer=PygmentsLexer(CommandLexer),
                                 complete_in_thread=True,
                                 mouse_support=True)
        except KeyboardInterrupt:
            print(f"{Fore.LIGHTGREEN_EX}Bye.")

            break

        if any(ipt.startswith(match) for match in ["#", "//", '"', ";"]):
            continue
        elif ipt.startswith("/*") and not ipt.endswith("*/"):
            error("This comment block must be enclosed in */")
        elif ipt.startswith("/*") and ipt.endswith("*/"):
            continue

        start = time.perf_counter()

        try:
            cmd_completer.run_action(ipt)
        except ValueError:
            error("Command not found.")

            continue
        except TypeError:
            error("Argument(s) missing or invalid.")

            continue

        end = time.perf_counter()

        ok(end - start)


def print_device(device_id: int, device) -> None:
    print(f"{Back.LIGHTBLUE_EX + Fore.BLACK}  DEVICE  ")
    print(f"    {Fore.GREEN}Id{Fore.RESET}: {Fore.LIGHTCYAN_EX + str(device_id) + Fore.WHITE + Style.DIM},")
    print(f"    {Fore.GREEN}Name{Fore.RESET}: {Fore.LIGHTCYAN_EX + str(device.friendly_name) + Fore.WHITE + Style.DIM},")
    print(f"    {Fore.GREEN}Model{Fore.RESET}: {Fore.LIGHTCYAN_EX + str(device.model_name)}")


def auto_select() -> None:
    global nowCast

    if len(casts) == 0:
        return

    nowCast = preCasts[0][0]

    print(f"{Back.LIGHTGREEN_EX + Fore.BLACK}  SUCCESS  {Back.RESET + Fore.LIGHTWHITE_EX} Device selected")
    nowCast.wait()


def is_url(url: str):
    if url in " ":
        return False

    return re.compile(r"^(http|https|ftp|blob)://").match(url)


def is_youtube(url: str):
    re.compile(r"^((https|http)://)?(www\.)?youtu(be|\.be)?(\.com)?").match(url)


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
    resp = requests.get(f"https://youtube.com/get_video_info?video_id={youtube_id}&asv=3&hl=en")

    if resp.status_code != 200:
        error(f"Youtube returned status {Fore.CYAN + str(resp.status_code)}")
        print(resp.text)

        return None

    param = {}

    for parm in resp.text.split("&"):
        lst = parm.split("=")

        if len(lst) != 2:
            continue

        param[lst[0]] = parse.unquote(lst[1])

    if "status" in param and param["status"] == "fail":
        error(f"Youtube response isn't includes {Fore.CYAN}status")

        return None

    if "player_response" in param:
        player_response = json.loads(param["player_response"])

        return {
            "url": player_response["streamingData"]["formats"][0]["url"],
            "mime": player_response["streamingData"]["formats"][0]["mimeType"]
        }


if __name__ == "__main__":
    init(autoreset=True)

    try:
        with open(f"{os.path.dirname(__file__)}/config.yml", 'r') as file:
            config = yaml.load(file, Loader=yaml.SafeLoader)
            if config is not None and "prompt" in config:
                prefix = f"{config['prompt']} "
    except FileNotFoundError:
        error(f"{os.path.dirname(__file__)}/config.yml not found.")

    if len(sys.argv) > 1:
        if any(match in sys.argv for match in ["--version", "--ver", "version", "ver", "-v"]):
            print("v2.0")
            exit(0)

        del sys.argv[0]

        if not con():
            exit(1)

        auto_select()
        cmd_completer.run_action(" ".join(sys.argv))
        exit(0)

    pretty_errors.configure(separator_character="*",
                            filename_display=pretty_errors.FILENAME_EXTENDED,
                            line_number_first=True,
                            display_link=True,
                            lines_before=5,
                            lines_after=2,
                            line_color=f"{pretty_errors.BRIGHT_RED}> {pretty_errors.default_config.line_color}",
                            code_color=f"  {pretty_errors.default_config.line_color}",
                            truncate_code=True,
                            display_locals=True)
    pretty_errors.activate()

    print(f"{Back.LIGHTBLUE_EX + Back.BLACK}  GoogleHome CLI  ")
    print(
        f"{Style.BRIGHT}Made by{Style.RESET_ALL}: P2P-Develop "
        f"[GitHub: \033[4m{Fore.LIGHTBLUE_EX}https://github.com/P2P-Develop{Style.RESET_ALL}]"
    )
    print(
        f"{Style.BRIGHT}Contribute in GitHub{Style.RESET_ALL}: \033[4m{Fore.LIGHTBLUE_EX}"
        f"https://github.com/P2P-Develop/GoogleHomeCLI"
    )
    print()

    con()
    command_thread = threading.Thread(target=wait_command)
    command_thread.setDaemon(True)
    auto_select()

    print(f"{Back.LIGHTGREEN_EX + Fore.BLACK}  READY  {Back.RESET + Fore.LIGHTWHITE_EX} GoogleHomeCLI is ready to start.")

    command_thread.start()
    command_thread.join()
