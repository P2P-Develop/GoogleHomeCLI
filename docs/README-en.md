# GoogleHomeCLI

[Overview](#overview) | [Usage](#usage) | [Commands](#commands) | [Configuration](#configuration) | [Contributing](CONTRIBUTING.md) | [Security](SECURITY.md) | [Package requirement](../requirements.txt) | [Thanks](#thanks)

<details>
<summary>Table of Contents</summary>

- [GoogleHomeCLI](#googlehomecli)
  - [Overview](#overview)
  - [Usage](#usage)
  - [Interactive comments](#interactive-comments)
  - [Commands](#commands)
    - [`echo`](#echo)
    - [`tts`](#tts)
      - [Aliases](#aliases)
    - [`exit`](#exit)
      - [Aliases](#aliases-1)
    - [`list`](#list)
      - [Aliases](#aliases-2)
    - [`kill`](#kill)
    - [`status`](#status)
      - [Alias](#alias)
    - [`reconnect`](#reconnect)
      - [Alias](#alias-1)
    - [`use <id|name>`](#use-idname)
      - [Alias](#alias-2)
    - [`play <path|link>`](#play-pathlink)
      - [Aliases](#aliases-3)
  - [Configuration](#configuration)
  - [Thanks](#thanks)

</details>

## Overview

Control Google Home (Chrome Cast) in any command-line.
This script can only use Python3, so Python2 isn't supported.
This script implemented internal command-line.
Please note that this project is released with a [Contributor Code of Conduct](CODE-OF-CONDUCT.md). By participating in this project you agree to abide by its terms.

## Usage

Python3 must be available to use this script.

1. Clone the repository.
   If you not avail `git`, download directory from GitHub and extract it.

   in HTTPS:

   ```bash
   $ git clone https://github.com/P2P-Develop/GoogleHomeCLI --depth 1
   ```

   in SSH:

   ```bash
   $ git clone git@github.com:P2P-Develop/GoogleHomeCLI --depth 1
   ```

   in [Github CLI](https://github.com/cli/cli):

   ```bash
   $ gh repo clone P2P-Develop/GoogleHomeCLI --depth 1
   ```

2. Access the cloned repository.

   ```bash
   $ cd GoogleHomeCLI
   ```

3. Install required packages.

   ```bash
   $ python3 -m pip install -r requirements.txt
   ```

4. Run script.
   ```bash
   $ python3 src/home.py
   ```

## Interactive comments

GoogleHomeCLI supports interactive comments.
You can use three symbols: `#`, `//`, and `"`.
If you do not start with these symbols, they will not be recognized as interactive comments.

## Commands

### `echo`

Prints characters to the console.
Expand quotation marks when printing if enclosed. The priority is `"`,`'`, \`.
Be careful not to forget enclosing when write it in quotation marks. It will be error when running.

### `tts`

Play Text-To-Speech from the selected device.
This command supported quotations like [`echo`](#echo).

#### Aliases

- `speak`
- `speech`
- `talk`

### `exit`

Exit the script.
The script can exit with ^C when prompt showing.

#### Aliases

- `bye`
- `stop`

### `list`

Show recognized devices.

#### Aliases

- `device`
- `devices`
- `ls`

### `kill`

Kill the selected device.

### `status`

List connected devices status.

#### Alias

- `show`

### `reconnect`

Reconnect devices.

#### Alias

- `rc`

### `use <id|name>`

Select specified id / name device.

#### Alias

- `select`

### `play <path|link>`

Play specified local file / Youtube URL from selected device.

#### Aliases

- `sound`
- `music`
- `p`

## Configuration

The Google Home CLI comes with a configuration file.
The file name is [`config.yml`](../src/config.yml) and an error will occur if the config file is not found.
The settings are as following:

|  Name  | Default value | Description                                     |
| :----: | :-----------: | :---------------------------------------------- |
| prompt |      ">"      | First prompt prefix when waiting for a command. |

## Thanks

- [Erik Cederstrand](https://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python) - The proper way to get the ID from Youtube URLs.
