from pathlib import Path
from typing import Union
from enum import Enum


class SelectionStrategy(Enum):
    ALPHABETICAL = "alphabetical"
    NEWEST = "newest"


def find(path: Union[Path, str, None] = None, strategy: SelectionStrategy = SelectionStrategy.NEWEST) -> tuple[str, str] | None:
    """Return a matching certificate and private key pair.

    The returned tuple is in the form ``(cert_file, key_file)`` so it can be
    passed directly to libraries such as ``requests`` that expect a client
    certificate pair.

    If ``path`` is omitted, the current working directory is searched. When a
    directory contains more than one matching pair, ``strategy`` controls which
    pair is selected.

    Args:
        path (Union[Path, str, None], optional): A certificate file, key file,
            or directory to search. If omitted, the current working directory is
            used.
        strategy (SelectionStrategy, optional): How to choose a pair when more
            than one matching certificate/key pair is found in a directory.
            ``SelectionStrategy.NEWEST`` picks the most recently modified
            certificate. ``SelectionStrategy.ALPHABETICAL`` picks the pair whose
            certificate filename sorts first.

    Returns:
        tuple[str, str] | None: The matching certificate and key paths, or
        ``None`` if no matching pair is found. The returned tuple is in the form
        ``(cert_file, key_file)`` so it can be passed directly to the``requests``
        library.
    """
    if path is None:
        path = Path.cwd()

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