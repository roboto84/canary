<h1 align="center">canary</h1>

<div align="center">
	<img src="assets/canary.png" width="250" title="canary logo">
</div>

## About
`canary` is a simple command line tool that recursively traverses a path given for all video, image, or text files of a specified criteria.

## Install
This project is managed with [Python Poetry](https://github.com/python-poetry/poetry). With Poetry installed correctly, simply clone this project and install its dependencies:

- Clone repo
    ```
    git clone https://github.com/roboto84/canary.git
    ```
    ```
    cd canary
    ```
- Install dependencies
    ```
    poetry install
    ```
- You also need `libmediainfo` on your system. If running Fedora, simply install with `dnf`:
    ```
    sudo dnf install libmediainfo
    ```

## Usage
- Run with the following options:
    ```
    poetry run python canary/canary.py <Action Type> <Directory> <Media Type> <Max Pixel Height: Optional>
    ```

## Options
| Title | Description | Options
|-------|-------------|---------
| Action Type |  | `list`, `table`, `delete`
| Directory | Directory you want to run `canary`. |
| Media Type | |`video`, `image`, `text`
| Max Pixel Height | Max pixel height for video or image searches. *(Optional)* |

## Examples
- Output a `table` view of all images in the `/home/roboto/Pictures` directory (recursively) that is less than `800`px in height.
    ```
    poetry run python canary/canary.py table /home/roboto/Pictures image 800
    ```
- Output a `list` view of all videos in the `/home/roboto` directory (recursively).
    ```
    poetry run python canary/canary.py list /home/roboto video
    ```


## Commit Conventions
Git commits follow [Conventional Commits](https://www.conventionalcommits.org) message style as explained in detail on their website.

<br/>
<sup>
    <a href="https://www.flaticon.com/free-icons/bird" title="bird icons">
        canary icon created by Freepik - Flaticon
    </a>
</sup>
