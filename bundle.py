#!/usr/bin/env python3

from pathlib import Path
import tarfile

ignored_files = ['src.tar.gz', '.DS_Store', 'Desktop.ini', 'desktop.ini', '.directory']
ignored_types = ['.pyc', '.pyo', '.pyd']
ignored_dirs = ['.git', '__pycache__', '.venv', 'venv', 'env', 'ENV', '.idea', '.vscode']


def bundle_filter(info: tarfile.TarInfo):
    path = Path(info.name)
    if info.isfile() and (path.name in ignored_files or path.suffix in ignored_types):
        return None
    elif info.isdir() and path.name in ignored_dirs:
        return None
    else:
        return info


def bundle():
    project_dir = Path(__file__).parent
    with tarfile.open('src.tar.gz', 'w:gz') as tar:
        tar.add(project_dir, arcname='.', filter=bundle_filter)


if __name__ == '__main__':
    bundle()
