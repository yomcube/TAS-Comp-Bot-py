# Quickstart

Navigate to the cloned project and install the required packages via `pip install -r requirements.txt`.

Create a file named `.env` in the project's root directory, then provide the following keys:

```
TOKEN = "Discord bot token, as a string"
WEATHER_API_KEY = API key for OpenWeatherMap, as an integer
DEFAULT = "Competition type, allowed values: mkw, sm64, as a string"
ENC_MUPEN_DIR = "Path to directory containing mupen exe"
ENC_AVI_DIR = "Path to avi and mp4 output directory"
ENC_SM64_SCRIPTS = "Semicolon-separated collection of paths to lua scripts to be ran when encoding"
ENC_MAX_QUEUE = "Maximum length of the encoding queue"
```

Then, run the main script via `python main.py`.