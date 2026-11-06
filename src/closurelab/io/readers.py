from pathlib import Path
from typing import Literal

from scipy.io.matlab import MatReadError, matfile_version


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

