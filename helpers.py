import errno
import os
from pathlib import Path
from typing import List

from illegal_file_system_operation import IllegalFileSystemOperation

MAIN_DRIVE = '/root'


def file_path(parent_path: str, name: str) -> str:
    """
    Get a file path given the parent path and name of the file system entity
    :param parent_path: str - The full string path of the parent
    :param name: str - The name of the file system entity
    :return: str - Full path of the file system entity
    """
    return os.path.join(parent_path, name)


def recursive_size_update(node) -> None:
    """
    Recursively update the size attribute upward through the file system tree
    :param node: FileSystemEntity
    """
    node.set_size()
    if hasattr(node, 'parent'):
        recursive_size_update(node.parent)


def calc_size(children: List, size: int = 0):
    """
    Calculate the size of the file system node (entity)
    :param children: List[FileSystemEntity] - list of file system nodes to calculate the size recursively
    :param size: int - the size of all file system nodes in the list, calculated recursively
    :return: size: int
    """
    for child in children.values():
        size += child.size

    return size


def get_parent_path_and_name(full_path: str):
    if not full_path:
        return None, None

    path = Path(full_path)
    parent_path = path.parent
    name = path.parts[-1]

    return parent_path, name


def valid_move_operation(dest_path: str, dest_name: str, dest_parent_node, source_path: str, source_node) -> bool:
    # Raise if attempting to move entity into itself
    if dest_parent_node == source_node:
        raise IllegalFileSystemOperation(errno.ENOENT, os.strerror(errno.ENOENT), dest_parent_node)
    # Raise if the source node or parent path doesn't exist
    if not source_node or not dest_parent_node:
        missing_path = source_path if not source_node else dest_path
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), missing_path)
    # Raise if destination path already exists
    if hasattr(dest_parent_node, 'children') and dest_parent_node.children.get(dest_name):
        raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), dest_path)

    return True

