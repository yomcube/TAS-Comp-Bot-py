# Quickstart

Navigate to the cloned project and install the required packages via `pip install -r requirements.txt`.

Edit the `.env` file in the project root and include the required fields.

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

Choose your desired encoding mode, depending on the use-case.

![grafik](https://github.com/crackhex/TAS-Comp-Bot-py/assets/48759429/63f25120-5fa5-407b-9b3e-c5a6b8ffe77d)

`External capture` - Captures the game. Requires a capable graphics plugin, but works regardless of window visibility and is much faster.

`Internal capture window` - Captures the game. Takes screenshots of the window, meaning it needs to be visible on-screen to be captured.

`Internal capture desktop` - Captures the game alongside Lua graphics. Takes screenshots of the desktop, meaning foreign windows may be captured.

> [!WARNING]  
> The `Internal capture desktop` mode may leak sensitive information if windows overlap Mupen64.

To prepare the avi preset, open a ROM and then start a video capture.

When prompted for a codec, select x264vfw and enable "Fast Decode" and "Zero Latency" in the configuration dialog.

Once the capture has started, let it run for a few frames and then stop it.

## Config

Close Mupen64 and open the `config.ini` file located in its directory.

Find the `silent_mode` key and change its value from `0` to `1`.

Find the `fps_modifier` key and change its value from `100` to `10000`.

For increased performance at the cost of stability loss on some games, set the value of `skip_rendering_lag` to `1`.
