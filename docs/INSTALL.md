# Installation Guide — forage-dj (Linux + Windows)

This guide covers easy installation on **Linux** (including WSL) and **Windows**.

The project is designed to work great on both operating systems with a single set of scripts.

## One-Command Recommendation (Works on Both)

From the `forage-dj` root directory:

```bash
# Best universal experience (Linux or Windows)
python scripts/install.py
python scripts/install.py --full     # if you want voice, stems, audio-tools extras
```

This script:
- Bootstraps `uv` (Astral) if needed
- Creates a `.venv`
- Installs dependencies
- Helps you pick a large storage location (Z: drive, D:/E:, etc.)
- Generates cross-platform helpers (`.grok/hf-cache.env` + `.grok/hf-cache.ps1`)
- Writes `.grok/paths.json` so the whole application finds your data
- Runs `doctor --heal`

---

## Linux / macOS / WSL (Traditional)

```bash
./scripts/setup.sh            # or
./scripts/setup.sh --full
```

Or just use the universal command above.

After running, activate the environment:

```bash
source .grok/hf-cache.env
source .venv/bin/activate
```

**Recommended system packages** (Ubuntu/Debian):

```bash
sudo apt update
sudo apt install libportaudio2 portaudio19-dev ffmpeg espeak-ng \
                 libsndfile1 build-essential python3-dev
```

For best low-latency audio also consider PipeWire or JACK.

---

## Windows (PowerShell)

1. Open **PowerShell** in the `forage-dj` folder (right-click → "Open in Terminal" or `cd` into it).

2. Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
# or with all extras:
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1 -Full
```

   (Or simply `python scripts/install.py --full`)

3. Activate in future sessions:

```powershell
. .grok\hf-cache.ps1
.venv\Scripts\Activate.ps1
```

### Windows-Specific One-Time Setup

- **Kokoro TTS** (the `speak` command) requires **eSpeak NG**:
  - Download the latest `.msi` installer from: https://github.com/espeak-ng/espeak-ng/releases
  - Run the installer (default options are fine).

- **Low-latency audio** (highly recommended for live mode):
  - Install **ASIO4ALL** (free): http://www.asio4all.org/
  - In many DAWs / sounddevice apps you can then select the ASIO driver.

- Some Python audio wheels benefit from the latest **Microsoft Visual C++ Redistributable** (usually already installed).

- MIDI: `python-rtmidi` works with the built-in Windows MIDI drivers. For pro controllers you may want the manufacturer's ASIO/MIDI drivers.

---

## After Installation (All Platforms)

```bash
uv run foragedj doctor --heal          # self-healing health check
uv run foragedj download-models        # (after accepting HF licenses for SA3 models)
uv run foragedj os                     # boot the retro Music Diffusion OS
uv run foragedj enhance --help
uv run foragedj speak "test voice" --voice af_heart
```

See also:
- `docs/MODEL_ACCESS.md` — gated model licenses + HF token
- `docs/ENHANCEMENT_TOOLS.md` — new AudioSR / FlashSR / LocalVQE / Kokoro usage
- `README.md`

---

## Relocating Data to a Large/Fast Drive Later

You can move everything later without reinstalling.

Set the environment variable **before** running commands:

**Linux / WSL / mac**:
```bash
export FORAGE_DJ_DATA_ROOT=/mnt/z/my-big-drive/forage-dj
```

**Windows (PowerShell)**:
```powershell
$env:FORAGE_DJ_DATA_ROOT = "D:\forage-dj-data"
```

Or re-run `python scripts/install.py` — it will let you pick a new location and update the helpers.

The `paths.py` module + `doctor` will respect this everywhere.

---

## Troubleshooting

- **PortAudio not found** (Linux): install `libportaudio2` + `portaudio19-dev` as shown above.
- **Kokoro crashes on Windows**: make sure eSpeak NG is installed and in PATH.
- **Slow downloads**: create a HF token and use `.grok/hf-cache.env` / `.ps1` + `export HF_TOKEN=...`
- **Real-time audio crackles on Windows**: use ASIO4ALL + set low buffer sizes in your audio apps.
- **MIDI not detected**: on Windows make sure your controller appears in the Windows MIDI settings / device manager.

Everything else is handled by the self-healing `doctor` command.

Welcome to the Sonic Forage Music Diffusion OS — now available on Linux and Windows. 🎛️
