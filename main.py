import datetime
import io
import re
import os
import shutil
import sys
import uuid
from typing import BinaryIO

from container_types import ContainerIndex, NotSupportedError, ContainerFile, ContainerFileList, FILETIME, Container
from savefile_types import SaveFile


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <save_file>")
        os.system("pause")
        exit(1)

    print("========== Starfield Save File Importer v0.0.5 ==========")
    print("WARNING: This tool is experimental. Always manually back up your existing saves!")
    print()

    # 1. find the container
    package_path = os.path.expandvars(r"%LOCALAPPDATA%\Packages\BethesdaSoftworks.ProjectGold_3275kfvn8vcwc")
    if not os.path.exists(package_path):
        print("Error: Could not find the package path. Make sure you have Xbox Starfield installed.")
        os.system("pause")
        exit(2)
    wgs_path = os.path.join(package_path, "SystemAppData", "wgs")
    container_regex = re.compile(r"[0-9A-F]{16}_[0-9A-F]{32}$")
    container_path = None
    for d in os.listdir(wgs_path):
        if container_regex.match(d):
            container_path = os.path.join(wgs_path, d)
            break
    if container_path is None:
        # not actually sure when this will not exist though
        print("Error: Could not find the container path. Please try to run the game once to create it.")
        os.system("pause")
        exit(2)
    print(f"Found container path: {container_path}")

    # 2. read the container index file
    container_index_path = os.path.join(container_path, "containers.index")
    container_index_file = open(container_index_path, "rb")
    try:
        container_index = ContainerIndex.from_stream(container_index_file)
    except NotSupportedError as e:
        print(f"Error: Detected unsupported container format, please report this issue: {e}")
        os.system("pause")
        exit(3)
    container_index_file.close()
    print("Parsed container index:")
    print(f"  Package name: {container_index.package_name}")
    print(f"  {len(container_index.containers)} containers:")
    for container in container_index.containers:
        print(f"    {container.container_name} ({container.size} bytes)")
    print()

    # 3. read the source save file
    source_save_path = sys.argv[1]
    if not os.path.exists(source_save_path):
        print(f"Error: Source save file does not exist: {source_save_path}")
        os.system("pause")
        exit(4)
    source_save_file = open(source_save_path, "rb")
    save_file = SaveFile.from_stream(source_save_file)
    source_save_file.close()
    print("Parsed save file:")
    print(f"  Filename: {save_file.filename}")
    print(f"  Uncompressed size: {save_file.uncompressed_size} bytes")
    print(f"  {len(save_file.chunks)} chunks")
    print()

    # 3.2 check if the save file already exists
    for container in container_index.containers:
        if container.container_name == f"Saves/{save_file.filename}":
            print(f"Error: Save file already exists: {container.container_name}")
            os.system("pause")
            exit(5)

    # 4. create a new container
    # 4.1 create container file list
    print("Creating new container")
    files = [
        ContainerFile("BETHESDAPFH", uuid.uuid4(), save_file.header_bytes()),
    ]
    for index, chunk in enumerate(save_file.chunks):
        files.append(ContainerFile(f"P{index}P", uuid.uuid4(), chunk.data))
    container_file_list = ContainerFileList(seq=1, files=files)

    # 4.2 create container index entry
    container_name = f"Saves/{save_file.filename}"
    container_uuid = uuid.uuid4()
    mtime = FILETIME.from_timestamp(os.path.getmtime(source_save_path))
    size = save_file.real_header_size + sum(chunk.size for chunk in save_file.chunks)
    container = Container(
        container_name=container_name,
        cloud_id="",
        seq=1,
        flag=5,
        container_uuid=container_uuid,
        mtime=mtime,
        size=size,
    )

    # 4.3 add new container to container index
    container_index.containers.append(container)
    container_index.mtime = FILETIME.from_timestamp(datetime.datetime.now().timestamp())

    # 4.4 cowardly creating a backup of the container
    container_backup_path = os.path.join(container_path, f"{container_path}.backup.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
    shutil.copytree(container_path, container_backup_path)
    print(f"Created backup of container: {container_backup_path}")

    # 4.5 write container file list
    container_content_path = os.path.join(container_path, container_uuid.bytes_le.hex().upper())
    os.makedirs(container_content_path, exist_ok=True)
    container_file_list.write_container(container_content_path)
    print(f"Wrote new container to {container_content_path}")

    # 4.6 write container index
    container_index.write_file(container_path)
    print("Updated container index")

    print("Done!")
    os.system("pause")


if __name__ == '__main__':
    main()