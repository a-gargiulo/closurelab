"""Readers for MATLAB .mat files in all format versions."""

from pathlib import Path
from typing import Literal, assert_never

import h5py
from scipy.io.matlab import MatReadError, matfile_version, whosmat

type MatInfo = dict[str, tuple[tuple[int, ...], str]]


def detect_mat_version(path: str | Path) -> Literal["v4", "v5", "v7.3"]:
    """Detect the format version of a MATLAB file.

    :param path: Path to the ``.mat`` file.
    :return: ``"v4"``, ``"v5"`` (MATLAB v5 to v7, compressed or not),
        or ``"v7.3"`` (HDF5-based).
    :raises FileNotFoundError: If ``path`` does not exist.
    :raises ValueError: If ``path`` is not a recognizable MATLAB file.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"MATLAB file not found: {path}")

    try:
        major, _ = matfile_version(path, appendmat=False)
    except (MatReadError, ValueError, IndexError) as err:
        # scipy raises IndexError for files shorter than the 128-byte
        # v5 header instead of its own MatReadError.
        raise ValueError(f"Not a recognizable MATLAB file: {path}") from err

    # scipy detects v4 heuristically (a zero byte among the first four),
    # so some non-MATLAB binary files may be misreported as "v4".
    if major == 0:
        return "v4"
    if major == 1:
        return "v5"
    if major == 2:
        return "v7.3"
    raise ValueError(f"Unsupported MATLAB file version {major}: {path}")


def inspect_mat(path: str | Path) -> MatInfo:
    """List the variables in a MATLAB file without loading their data.

    :param path: Path to the ``.mat`` file.
    :return: Mapping from each variable name to its shape and MATLAB class,
        e.g. ``{"U": ((128, 96, 500), "double")}``. Shapes follow MATLAB's
        dimension order for every file format.
    :raises FileNotFoundError: If ``path`` does not exist.
    :raises ValueError: If ``path`` is not a recognizable MATLAB file.
    """
    path = Path(path)
    version = detect_mat_version(path)

    match version:
        case "v4" | "v5":
            return _inspect_scipy(path)
        case "v7.3":
            return _inspect_hdf5(path)
        case _:
            assert_never(version)


def _inspect_scipy(path: Path) -> MatInfo:
    """List variables in a v4 or v5 MATLAB file using scipy."""
    # chars_as_strings=False reports char arrays in MATLAB's shape
    # (e.g. (1, 4) for 'tiny') rather than scipy's converted shape (1,).
    return {
        name: (shape, mclass)
        for name, shape, mclass in whosmat(path, chars_as_strings=False)
    }


def _hdf5_shape(obj: h5py.Dataset | h5py.Group) -> tuple[int, ...]:
    """Return a v7.3 variable's shape in MATLAB's dimension order."""
    if isinstance(obj, h5py.Group):
        if "MATLAB_fields" in obj.attrs:  # scalar struct
            return (1, 1)
        # Struct array: each field holds one reference per element.
        first_field = next(iter(obj.values()))
        return first_field.shape[::-1]
    if obj.attrs.get("MATLAB_empty", 0):
        # Empty arrays store their dimensions as data, already in MATLAB order.
        return tuple(int(d) for d in obj[()])
    return obj.shape[::-1]


def _inspect_hdf5(path: Path) -> MatInfo:
    """List variables in a v7.3 MATLAB file using h5py.

    Shapes are converted to MATLAB's dimension order, since MATLAB writes
    column-major data that h5py reads as row-major.
    """
    info: MatInfo = {}
    with h5py.File(path, "r") as f:
        for name, obj in f.items():
            if name.startswith("#"):  # MATLAB internals, e.g. #refs#
                continue
            info[name] = (_hdf5_shape(obj), obj.attrs["MATLAB_class"].decode())
    return info
