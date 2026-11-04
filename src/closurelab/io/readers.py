from pathlib import Path

from scipy.io.matlab import MatReadError, matfile_version

def detect_mat_version(path: str | Path) -> str:
    """Detect which reader a MATLAB file needs.

    :param path: Path to the ``.mat`` file.
    :return: ``"v5"`` for files scipy can read (v4 to v7, compressed or
        not), ``"v7.3"`` for HDF5-based files.
    :raises FileNotFoundError: If ``path`` does not exist.
    :raises ValueError: If ``path`` is not a recognizable MATLAB file.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"MATLAB file not found: {path}")

    try:
        major, _ = matfile_version(path, appendmat=False)
    except (MatReadError, ValueError, IndexError) as err:
        raise ValueError(f"Not a recognizable MATLAB file: {path}") from err

    if major in (0, 1):
        return "v5"
    if major == 2:
        return "v7.3"
    raise ValueError(f"Unsupported MATLAB file version {major}: {path}")
