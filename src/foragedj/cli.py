"""CLI entrypoint for forage-dj (placeholder for MVP)"""

import argparse

def main():
    parser = argparse.ArgumentParser(description="Sonic Forage DJ - AI Autonomous DJ")
    parser.add_argument("--version", action="version", version="0.1.0")
    parser.add_argument("--gui", action="store_true", help="Launch Dear PyGui interface (default)")
    parser.add_argument("--midi-learn", action="store_true", help="Enter MIDI learn mode")
    args = parser.parse_args()

    print("🎧 forage-dj v0.1.0 - Sonic Forage Autonomous DJ")
    print("Repo: https://github.com/Sonic-Forage/forage-dj")
    print("Status: Foundation complete. See docs/AGENTIC_BUILD_PLAN.md to start building Phase 1.")
    print("\nNext: uv sync && uv run foragedj --gui")

if __name__ == "__main__":
    main()
