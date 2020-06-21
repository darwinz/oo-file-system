import os
from typing import List

MAIN_DRIVE = '/root'


def file_path(parent_path: str, name: str):
    """
    Get a file path given the parent path and name of the file system entity
    :param parent_path: str - The full string path of the parent
    :param name: str - The name of the file system entity
    :return: str - Full path of the file system entity
    """
    return os.path.join(parent_path, name)


def recursive_size_update(node):
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
