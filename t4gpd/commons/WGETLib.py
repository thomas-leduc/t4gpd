"""
Created on 04 May 2026

@author: tleduc

Copyright 2020-2026 Thomas Leduc

This file is part of t4gpd.

t4gpd is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

t4gpd is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with t4gpd.  If not, see <https://www.gnu.org/licenses/>.
"""

import requests
import sys
from pathlib import Path


class WGETLib(object):
    """
    classdocs
    """

    CHUNK_SIZE = 1024 * 1024  # 1 MB per block

    @staticmethod
    def download(url: str, dest_dir: str) -> None:
        """
        Download a file from the given URL to the specified destination directory.
        Resumable download feature (equivalent to "wget --continue").
        If the destination file already exists and is incomplete, resume the
        download from the missing byte (HTTP Range). If the file is complete
        (local size == Content-Length), ignore it.
        :param url: The URL of the file to download.
        :param dest_dir: The directory where the file should be saved.
        :return: None
        """
        dest_dir = Path(dest_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        filename = url.split("/")[-1]
        dest_path = dest_dir / filename

        # ---  Size already downloaded ---
        local_size = dest_path.stat().st_size if dest_path.exists() else 0

        headers = {}
        if local_size > 0:
            headers["Range"] = f"bytes={local_size}-"

        response = requests.get(url, headers=headers, stream=True, timeout=60)

        # 416: Invalid range => The file is already complete
        if response.status_code == 416:
            print(f"[OK] {filename} --- already downloaded, ignored.")
            return

        # 200 : The server returns everything (no data retrieved or file not found)
        # 206 : accepted return
        if response.status_code not in (200, 206):
            print(
                f"[ERROR] {filename} --- unexpected HTTP status code: {response.status_code}",
                file=sys.stderr,
            )
            response.raise_for_status()

        # Check: Does the server actually support failover?
        resuming = response.status_code == 206
        if local_size > 0 and not resuming:
            # Server does not support Range => Start over
            print(
                f"[WARN] {filename} --- the server does not support resuming. Restarting."
            )
            local_size = 0

        total = int(response.headers.get("Content-Length", 0)) + local_size
        mode = "ab" if resuming else "wb"

        print(
            f"[{'RESUMING' if resuming else 'START  '}] {filename}"
            + (f" ({local_size / 1e6:.1f} MB ALREADY DOWNLOADED)" if resuming else "")
            + (f" — total : {total / 1e6:.1f} MB" if total else "")
        )

        downloaded = local_size
        with open(dest_path, mode) as f:
            for chunk in response.iter_content(chunk_size=WGETLib.CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded / total * 100
                        print(
                            f"\r  {pct:5.1f} %  ({downloaded / 1e6:.1f} / {total / 1e6:.1f} MB)",
                            end="",
                            flush=True,
                        )

        print(f"\n[COMPLETED] {filename}")
