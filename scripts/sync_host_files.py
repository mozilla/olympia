#!/usr/bin/env python3

import json
import os
import subprocess
from pathlib import Path


def sync_host_files():
    BUILD_INFO = os.environ.get('BUILD_INFO')
    HOME = os.environ.get('HOME')
    subprocess.run(['make', 'update_deps'], check=True)

    with open(BUILD_INFO, 'r') as f:
        build_info = json.load(f)

    if build_info.get('target') == 'production':
        subprocess.run(['make', 'compile_locales'], check=True)
        subprocess.run(['make', 'update_assets'], check=True)
    else:
        for path in ['static-build', 'site-static']:
            path = Path(HOME) / path
            subprocess.run(['make', 'clean_directory', f"ARGS='{path}'"], check=True)


if __name__ == '__main__':
    sync_host_files()
