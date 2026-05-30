"""Tests for the full setlist 'walk away' generation feature.
Validates manifest loading + dry-run library output (including new walkaway artifacts).
"""

from pathlib import Path
import tempfile
import json

import pytest

from foragedj.setlist import load_manifest, generate_setlist


def test_manifest_loading():
    manifest = load_manifest(Path("setlists/bassline_dominion_seed424242.yaml"))
    assert manifest["seed"] == 424242
    assert len(manifest["tracks"]) == 6
    assert "Bass House" in manifest["theme"]
    # Also test the alt manifest quickly
    m2 = load_manifest(Path("setlists/bassline_dominion_seed777777.yaml"))
    assert m2["seed"] == 777777


def test_dry_run_setlist_generation():
    """Basic validation of the core walk-away generator in dry mode (no real models needed)."""
    manifest = Path("setlists/bassline_dominion_seed777777.yaml")

    with tempfile.TemporaryDirectory() as tmp:
        output_root = Path(tmp) / "libraries"
        library = generate_setlist(manifest, output_root=output_root, dry=True)

        assert library.seed == 777777
        assert len(library.tracks) == 6
        assert library.library_dir  # new field for accurate path reporting

        # New clean folder naming (no ugly _-_ or leftover parens)
        expected_dir = output_root / "Bassline_Dominion_Alternate_Universe_Seed777777"
        assert str(library.library_dir).endswith("Bassline_Dominion_Alternate_Universe_Seed777777")

        # library.json written with rich new walkaway data
        lib_json = expected_dir / "library.json"
        assert lib_json.exists()

        data = json.loads(lib_json.read_text())
        assert data["seed"] == 777777
        assert len(data["tracks"]) == 6
        assert "harmonic_suggestions" in data
        assert "energy_estimates" in data
        assert "recommended_transitions" in data
        assert isinstance(data["recommended_transitions"], dict)
        # At least one transition suggestion should exist
        assert any(len(v) > 0 for v in data["recommended_transitions"].values())

        # playlist.txt for DJ software (the key new artifact)
        pl = expected_dir / "playlist.txt"
        assert pl.exists()
        content = pl.read_text()
        assert "Bassline Dominion" in content
        assert "playlist.txt" not in content  # no self ref
        assert "Seed 777777" in content or "seed 777777" in content.lower()
        # Contains the wav filenames in order
        assert "01_777777.wav" in content or "1_777777.wav" in content  # tolerant of padding during transition
