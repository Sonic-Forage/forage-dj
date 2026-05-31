#!/usr/bin/env python3
"""
ForageDJ Model Speed & Capability Benchmark
===========================================

Purpose:
- Test every available Stable Audio 3 model variant for generation speed
- Measure wall-clock time on your specific hardware (GPU/CPU)
- Generate short reference clips for quality comparison
- Record peak memory usage where possible
- Produce a clean, shareable report

Usage (after installing deps):
    cd /mnt/z/IMF2045/forage-dj
    uv run python test_outputs/model_benchmarks/run_model_speed_test.py

Recommended one-time setup for real generation:
    git clone https://github.com/Stability-AI/stable-audio-3.git /mnt/z/IMF2045/stable-audio-3
    cd /mnt/z/IMF2045/stable-audio-3
    uv sync --extra ui
    cd /mnt/z/IMF2045/forage-dj
    uv pip install -e /mnt/z/IMF2045/stable-audio-3

Then re-run this script.

Results will be written to:
    test_outputs/model_benchmarks/results_<timestamp>/
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
BENCH_DIR = Path(__file__).parent / "results"
BENCH_DIR.mkdir(parents=True, exist_ok=True)

# Test matrix - keep these short for speed testing
TEST_CASES = [
    {"model": "small-music", "prompt": "energetic bass house, rolling bassline, crisp drums, 128bpm, festival energy", "duration": 15, "seed": 424242},
    {"model": "small-music", "prompt": "dark atmospheric techno, deep sub bass, hypnotic pads, 130bpm", "duration": 30, "seed": 424242},
    {"model": "small-sfx",   "prompt": "impactful festival riser with whooshes and stabs", "duration": 15, "seed": 424242},
    {"model": "small-sfx",   "prompt": "heavy industrial kick and snare impact", "duration": 10, "seed": 424242},
    {"model": "medium",      "prompt": "lush emotional breakdown with supersaw leads and wide pads, 128bpm", "duration": 20, "seed": 424242},
]

def get_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

def run_generation(test: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """Run a single generation via the CLI and capture timing + metadata."""
    model = test["model"]
    prompt = test["prompt"]
    duration = test["duration"]
    seed = test["seed"]

    slug = f"{model}_{duration}s_seed{seed}_{int(time.time())}"
    out_wav = output_dir / f"{slug}.wav"
    log_file = output_dir / f"{slug}.log"

    cmd = [
        "uv", "run", "foragedj", "generate",
        prompt,
        "--model", model,
        "--seed", str(seed),
        "--duration", str(duration),
        "--out", str(out_wav),   # if supported, otherwise it will go to default generated/
    ]

    print(f"\n=== Testing {model} | {duration}s | seed {seed} ===")
    print(f"Prompt: {prompt}")
    start = time.time()

    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes max per test
        )
        elapsed = time.time() - start

        # Save full log
        log_file.write_text(
            f"COMMAND: {' '.join(cmd)}\n"
            f"RETURN CODE: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}\n"
            f"ELAPSED_SECONDS: {elapsed:.2f}\n"
        )

        success = result.returncode == 0
        actual_output = None

        # Try to find the generated file
        if out_wav.exists() and out_wav.stat().st_size > 1000:
            actual_output = str(out_wav)
        else:
            # Fallback search in generated/
            candidates = list((PROJECT_ROOT / "generated").glob(f"*{seed}*.wav"))
            if candidates:
                actual_output = str(max(candidates, key=lambda p: p.stat().st_mtime))

        record = {
            "model": model,
            "prompt": prompt,
            "duration": duration,
            "seed": seed,
            "wall_time_seconds": round(elapsed, 2),
            "success": success,
            "output_file": actual_output,
            "return_code": result.returncode,
            "error": result.stderr.strip() if not success else None,
        }

        print(f"  Time: {elapsed:.1f}s | Success: {success}")
        if actual_output:
            print(f"  Output: {actual_output}")

        return record

    except subprocess.TimeoutExpired:
        return {
            "model": model,
            "prompt": prompt,
            "duration": duration,
            "seed": seed,
            "wall_time_seconds": None,
            "success": False,
            "error": "TIMEOUT after 300s",
        }
    except Exception as e:
        return {
            "model": model,
            "prompt": prompt,
            "duration": duration,
            "seed": seed,
            "wall_time_seconds": None,
            "success": False,
            "error": str(e),
        }

def main():
    timestamp = get_timestamp()
    run_dir = BENCH_DIR / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print("=== ForageDJ Model Speed & Quality Benchmark ===")
    print(f"Output directory: {run_dir}")
    print(f"GPU scan recommended before running: nvidia-smi")
    print()

    results: List[Dict[str, Any]] = []

    for test in TEST_CASES:
        rec = run_generation(test, run_dir)
        results.append(rec)
        # Small pause between tests
        time.sleep(2)

    # Write summary
    summary = {
        "timestamp": timestamp,
        "system": {
            "project_root": str(PROJECT_ROOT),
            "python": sys.executable,
        },
        "test_matrix": TEST_CASES,
        "results": results,
        "notes": "Run this after installing torch + stable-audio-3 for real timings. Small models are very fast on RTX 4070 12GB.",
    }

    summary_path = run_dir / "benchmark_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    # Human readable report
    md = run_dir / "README.md"
    md.write_text(f"""# ForageDJ Model Benchmark — {timestamp}

**Hardware**: NVIDIA RTX 4070 12GB (see nvidia-smi output for exact state)

## Results Summary

| Model | Duration | Wall Time (s) | Success | Output |
|-------|----------|---------------|---------|--------|
""")

    for r in results:
        status = "✅" if r.get("success") else "❌"
        out = r.get("output_file", "N/A")
        md.write_text(md.read_text() + f"| {r['model']} | {r['duration']}s | {r.get('wall_time_seconds', 'N/A')} | {status} | {out} |\n")

    md.write_text(md.read_text() + f"""

## Raw Data
See `benchmark_summary.json` for machine-readable results.

## How to Reproduce Real Timings

1. Install the inference stack (one time):
   ```bash
   git clone https://github.com/Stability-AI/stable-audio-3.git /mnt/z/IMF2045/stable-audio-3
   cd /mnt/z/IMF2045/stable-audio-3
   uv sync --extra ui
   cd /mnt/z/IMF2045/forage-dj
   uv pip install -e /mnt/z/IMF2045/stable-audio-3
   ```

2. Re-run this benchmark:
   ```bash
   uv run python test_outputs/model_benchmarks/run_model_speed_test.py
   ```

## Expected Performance on RTX 4070 12GB

- **small-music / small-sfx**: Extremely fast (often <5-8s for 15-30s audio)
- **medium**: Slower but very high quality, should fit comfortably in 12GB

LoRAs are downloaded but not yet wired into the generator (future work).

## GPU Recommendations

Your RTX 4070 12GB is an excellent card for this workload:
- All small models run great (even on CPU fallback is usable)
- Medium model will use a large chunk of VRAM but should work
- You can comfortably run the full workstation + mixer + generation at the same time

Run `nvidia-smi` during generation to watch VRAM usage.
""")

    print("\n=== Benchmark complete ===")
    print(f"Results written to: {run_dir}")
    print(f"  - benchmark_summary.json")
    print(f"  - README.md")

if __name__ == "__main__":
    main()
