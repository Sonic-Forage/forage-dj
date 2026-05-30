# scripts/

Helper automation for forage-dj.

## setup.sh

The canonical way to get a working `uv` environment on a fresh clone (Linux, macOS, WSL).

```bash
./scripts/setup.sh          # CPU + GUI + dev tools (recommended)
./scripts/setup.sh --full   # + voice + stems
```

It:
- Bootstraps `uv` if missing
- Installs common Linux audio dev packages (PortAudio, JACK, ffmpeg, etc.)
- Runs the correct `uv sync` for the chosen profile
- Invokes `foragedj doctor` at the end

See the script header for all flags.
