from pathlib import Path


def resolve_path(base: str | Path, path: str | Path):
    path = Path(path)
    base_path = Path(base).resolve()

    if path.is_absolute():
        return path.resolve()

    return (base_path / path).resolve()

def is_within_directory(path: str | Path, directory: str | Path) -> bool:
    try:
        Path(path).resolve().relative_to(Path(directory).resolve())
        return True
    except ValueError:
        return False

def display_path_rel_to_cwd(path: str, cwd: Path) -> str:
    try:
        p = Path(path)
    except Exception:
        return path
    
    if cwd:
        try:
            return str(p.relative_to(cwd))
        except ValueError:
            return str(p)
    
    return str(p)

def ensure_parent_directory(path: str | Path) -> Path:
    path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def is_binary_file(path: str | Path) -> bool:
    try:
        with open(path, 'rb') as f:
            chunk = f.read(8192)
            return b"\x00" in chunk 
    
    except (OSError, IOError):
        return False
