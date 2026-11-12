"""Tests for closurelab.io.readers."""

from pathlib import Path

import numpy as np
import pytest
from scipy.io import savemat

from closurelab.io.readers import detect_mat_version, inspect_mat

DATA_DIR = Path(__file__).parent / "data"
FIXTURES = ["tiny_v6.mat", "tiny_v7.mat", "tiny_v73.mat"]

# Expected contents of the fixtures, matching tests/data/make_fixtures.m.
FIXTURE_INFO = {
    "A": ((3, 4), "double"),
    "B": ((2, 3, 4), "double"),
    "N": ((3, 4), "double"),
    "X": ((3, 4), "double"),
    "Y": ((3, 4), "double"),
    "dt": ((1, 1), "double"),
    "name": ((1, 4), "char"),
    "mask": ((3, 4), "logical"),
    "E": ((0, 3), "double"),
    "S": ((1, 1), "struct"),
    "F": ((1, 3), "struct"),
}


# -- detect_mat_version ------------------------------------------------------


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("tiny_v6.mat", "v5"),
        ("tiny_v7.mat", "v5"),
        ("tiny_v73.mat", "v7.3"),
    ],
)
def test_detect_mat_version(filename, expected):
    assert detect_mat_version(DATA_DIR / filename) == expected


def test_detect_mat_version_v4(tmp_path):
    # MATLAB can no longer write v4 files, so scipy creates one here.
    path = tmp_path / "a.mat"
    savemat(path, {"A": np.ones((3, 4))}, format="4")
    assert detect_mat_version(path) == "v4"


def test_detect_mat_version_accepts_str():
    assert detect_mat_version(str(DATA_DIR / "tiny_v6.mat")) == "v5"


def test_detect_mat_version_raises_on_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="missing.mat"):
        detect_mat_version(tmp_path / "missing.mat")


@pytest.mark.parametrize(
    "content",
    [b"", b"abc", b"short text, not MATLAB", b"x" * 200],
    ids=["empty", "tiny", "short", "long"],
)
def test_detect_mat_version_raises_on_invalid_file(tmp_path, content):
    path = tmp_path / "bad.mat"
    path.write_bytes(content)
    with pytest.raises(ValueError, match="bad.mat"):
        detect_mat_version(path)


@pytest.mark.xfail(
    reason="scipy treats any file with a zero byte in the first 4 as v4",
    strict=True,
)
def test_detect_mat_version_rejects_binary_with_zero_byte(tmp_path):
    path = tmp_path / "bad.mat"
    path.write_bytes(b"AB\x00D" + b"x" * 200)
    with pytest.raises(ValueError):
        detect_mat_version(path)


# -- inspect_mat -------------------------------------------------------------


@pytest.mark.parametrize("filename", FIXTURES)
def test_inspect_mat(filename):
    assert inspect_mat(DATA_DIR / filename) == FIXTURE_INFO


def test_inspect_mat_v4(tmp_path):
    path = tmp_path / "a.mat"
    savemat(path, {"A": np.ones((3, 4))}, format="4")
    assert inspect_mat(path) == {"A": ((3, 4), "double")}


def test_inspect_mat_raises_on_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        inspect_mat(tmp_path / "missing.mat")
