from pathlib import Path
from typing import Union
from enum import Enum


class SelectionStrategy(Enum):
    ALPHABETICAL = "alphabetical"
    NEWEST = "newest"


DEFAULT_PATH = Path.cwd()


def find(path: Union[Path, str] = DEFAULT_PATH, strategy: SelectionStrategy = SelectionStrategy.NEWEST) -> tuple[str, str] | None:
    """Find the matching certificate and private key files for a given path.

    Returns a tuple (cert, key) or None.

    The goal is to make a tuple that you can directly use with requests' cert argument, which expects (cert_file, key_file).

    Args:
        path (Union[Path, str]): The path to the certificate file, key file, or a directory containing the certificate and key files.
        strategy (SelectionStrategy, optional): The strategy to use when multiple certificate-key pairs are found in a directory. Defaults to SelectionStrategy.NEWEST. The "newest" strategy selects the most recently modified certificate file, while the "alphabetical" strategy selects the certificate file that comes first when using string sort order.
    Returns:
        tuple[str, str] | None: A tuple containing the paths to the certificate and private key files, or None if no matching files are found.
    """
    if isinstance(path, str):
        path = Path(path)
    
    if "~" in str(path):
        path = path.expanduser()

    if path.is_file():
        cert_file = path.with_suffix('.crt')
        key_file = path.with_suffix('.key')
        if key_file.is_file() and cert_file.is_file():
            return str(cert_file), str(key_file)
    elif path.is_dir():
        candidates = []
        for file in path.iterdir():
            if not file.is_file():
                continue
            if file.name == "CAs.crt":
                continue
            if file.suffix == '.crt':
                cert_file = file
                key_file = file.with_suffix('.key')
                if key_file.is_file() and cert_file.is_file():
                    pair = cert_file, key_file
                    candidates.append(pair)
        if len(candidates) == 0:
            return None
        if len(candidates) == 1:
            cert, key = candidates[0]
            return str(cert), str(key)
        "If we made it this far then there are multiple candidates. We need to apply the selection strategy to pick one."
        if strategy == SelectionStrategy.ALPHABETICAL:
            candidates.sort(key=lambda pair: pair[0].name)
        elif strategy == SelectionStrategy.NEWEST:
            "The 'NEWEST' strategy selects the most recently modified certificate file."
            "We check the cert file because that's the one that can expire and is more likely to be updated."
            candidates.sort(key=lambda pair: pair[0].stat().st_mtime, reverse=True)
        cert, key = candidates[0]
        return str(cert), str(key)
    return None