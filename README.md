# Quickstart

First, just in case you dont have python, download the latest version [here](https://www.python.org/downloads/) and set it up.

Then navigate to the cloned project and install the required packages via `pip install -r requirements.txt`.

Create a `.env` file in the project root and paste this:
```py
# The bot's token
TOKEN = ""

# (optional) API key for OpenWeatherMap (as integer) (for a weather command)
WEATHER_API_KEY = 

# The competition type. Valid values: mkw, sm64
DEFAULT = "mkw"

# The directory which the bot downloads files to
DOWNLOAD_DIR = ""

# The mupen directory containing mupen64.exe 
ENC_MUPEN_DIR = ""

# The output directory for encoded movies
ENC_AVI_DIR = ""

# Semicolon-separated list of lua scripts to run when encoding
ENC_SM64_SCRIPTS = ""

# The maximum length of the encoding queue
ENC_MAX_QUEUE = "5"

# The directory which contains the bot database files
DB_DIR="database/"
```
Fill the fields with what you need

Then, run the main script via `python main.py`.

# Encoding

The N64 automated encoding module (`$encode`) requires additional setup.

## Prelude

First, download and install the [x264vfw](https://sourceforge.net/projects/x264vfw/) codec.

Ensure that the `ENC_MUPEN_DIR` environment variable has been set to a directory containing mupen64.exe,
`ENC_AVI_DIR` to a directory for movie output, and `ENC_SM64_SCRIPTS` contains your desired lua scripts.

## Mupen

> [!NOTE]  
> Mupen64 1.1.8 or higher is required for automated encoding.

Perform the initial setup of the Mupen64 1.1.8 installation by selecting plugins and adding a rom directory.

To prepare the avi preset, open a ROM and then start a video capture.

When prompted for a codec, select x264vfw and enable "Fast Decode" and "Zero Latency" in the configuration dialog.

Once the capture has started, let it run for a few frames and then stop it.

## Config

Close Mupen64 and open the `config.ini` file located in its directory.

Find the `silent_mode` key and change its value from `0` to `1`.

Find the `fps_modifier` key and change its value from `100` to `10000`.

For increased performance at the cost of stability loss on some games, set the value of `skip_rendering_lag` to `1`.
