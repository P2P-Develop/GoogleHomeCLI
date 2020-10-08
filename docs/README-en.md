# GoogleHomeCLI

[Overview](#overview) | [Usage](#usage) | [Commands](#commands) | [Thanks](#thanks)

# Overview

Control Google Home (Chrome Cast) in any command-line.
This script can only use Python3, so Python2 isn't supported.
This script implemented internal command-line.

# Usage

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

# Commands

## `exit`

Exit the script.
~~The script can exit with ^C.~~ [This is not working.](https://github.com/P2P-Develop/GoogleHomeCLI/issues/2)

### Aliases

-   `bye`
-   `stop`

## `list`

Show recognized devices.

### Aliases

-   `device`
-   `devices`
-   `ls`

## `kill`

Kill the process.

## `status`

List connected devices status.

### Alias

-   `show`

## reconnect

Reconnect devices.

### Alias

-   `rc`

## `use <id|name>`

Select specified id / name device.

### Alias

-   `select`

## `play <path|link>`

Play specified local file / Youtube URL from selected device.

### Aliases

-   `sound`
-   `music`
-   `p`

# Thanks

-   [Erik Cederstrand](https://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python) - The proper way to get the ID from Youtube URLs.
