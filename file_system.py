import errno
import os
from typing import List, Dict

from entity_types_enum import EntityTypes
from helpers import file_path, SEPARATOR, recursive_size_update
from file_system_entities import FileSystemNode, Drive, Folder, TextFile, ZipFile
from illegal_file_system_operation import IllegalFileSystemOperation
from not_a_text_file_error import NotATextFileError

MAIN_DRIVE = 'C:'


class FileSystem:
    def __init__(self):
        """
        Initialize the File System instance
        """
        self.drives: Dict[str, FileSystemNode] = {
            MAIN_DRIVE: Drive(EntityTypes.DRIVE.value, MAIN_DRIVE)
        }

    def create(self, type: int, name: str, parent_path: str) -> FileSystemNode:
        """
        Creates a file system node (entity)
        :param type: int - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param parent_path: str - Path of the parent file system node (entity)
        :return: FileSystemNode
        :raises FileNotFoundError, FileExistsError, IllegalFileSystemOperation
        """
        parent_path = rf'{parent_path}' if parent_path else None
        new_entity = None
        # Find the parent node from the parent path string
        parent_node = self.find_node_by_path(parent_path)

        # If the parent path doesn't exist
        if not parent_node:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), parent_path)
        # If object to be created already exists
        if hasattr(parent_node, 'children') and parent_node.children.get(name):
            raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), file_path(parent_node.path, name))

        try:
            if type == EntityTypes.FOLDER.value:
                new_entity = Folder(EntityTypes.FOLDER.value, name, parent_node)
            elif type == EntityTypes.TEXT_FILE.value:
                new_entity = TextFile(EntityTypes.TEXT_FILE.value, name, parent_node)
            elif type == EntityTypes.ZIP_FILE.value:
                new_entity = ZipFile(EntityTypes.ZIP_FILE.value, name, parent_node)
            self.insert_node(new_entity, parent_node)
        except IllegalFileSystemOperation:
            print('There was a problem creating the entity')

        return new_entity

    def delete(self, path: str) -> bool:
        path = rf'{path}'
        parent_path, name = self.get_parent_path_and_name(path)
        parent_node = self.find_node_by_path(parent_path)
        if parent_node and hasattr(parent_node, 'children'):
            if name in parent_node.children and parent_node.children[name]:
                del parent_node.children[name]
                return True
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

    def move(self, source_path: str, dest_path: str) -> FileSystemNode:
        source_path = rf'{source_path}'
        dest_path = rf'{dest_path}'
        # Get the destination parent path and the destination name
        dest_parent_path, dest_name = self.get_parent_path_and_name(dest_path)
        source_node = self.find_node_by_path(source_path)
        dest_parent_node = self.find_node_by_path(dest_parent_path)

        # If the parent path doesn't exist
        if not source_node or not dest_parent_node:
            missing_path = source_path if not source_node else dest_path
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), missing_path)
        # If destination path already exists
        if hasattr(dest_parent_node, 'children') and dest_parent_node.children.get(dest_name):
            raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), dest_path)

        new_entity = self.create(source_node.type, dest_name, dest_parent_path)
        self.delete(source_path)
        return new_entity

    def write_to_file(self, path: str, content: str) -> TextFile:
        path = rf'{path}'
        file_entity = self.find_node_by_path(path)
        # If the file system entity is not found
        if not file_entity:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)
        # If the file system entity is not a TextFile instance
        if not isinstance(file_entity, TextFile):
            raise NotATextFileError('Error => Not a text file')

        file_entity.content = content
        file_entity.size = len(content)
        recursive_size_update(file_entity)
        return file_entity

    ###########################
    # #### Helper methods #####
    ###########################

    def get_root_node(self):
        return self.drives[MAIN_DRIVE]

    @staticmethod
    def get_parent_path_and_name(full_path: str):
        if not full_path:
            return None, None
        path_parts = full_path.split(SEPARATOR)
        # The name of the entity is the last part
        name = path_parts[-1]
        # Combine the path parts except the name to get the parent path
        parent_path = rf'{SEPARATOR}'.join(path_parts[:-1])
        return parent_path, name

    @staticmethod
    def insert_node(entity: FileSystemNode, parent_node: FileSystemNode) -> None:
        """
        Insert a node entity as a child of parent_node
        :param entity: FileSystemNode - The node entity to be inserted
        :param parent_node: FileSystemNode - The node entity to receive a new child
        """
        if not hasattr(parent_node, 'children'):
            raise IllegalFileSystemOperation('Parent cannot contain any other entity')

        if entity.name in parent_node.children:
            raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), file_path(parent_node.path, entity.name))

        parent_node.children[entity.name] = entity

    def find_node_by_path(self, path: str):
        """
        Find the parent node based on its file path
        :param path: str - The full path of the node (entity) to be located
        :return: FileSystemNode - The file system node (entity)
        """
        path = rf'{path}' if path else None
        path_parts = path.split(SEPARATOR)
        return self.find_descendant_node(self.drives[MAIN_DRIVE], path_parts, path)

    def find_descendant_node(self, node: FileSystemNode, path_parts: List[str], path: str):
        """
        Recursively traverse children of a file system node to find a given node by path
        :param node: FileSystemNode - The file system node (entity) to be searched
        :param path_parts: List[str] - The list of path parts (found by splitting full path by the SEPARATOR)
        :param path: str - The full path of the node (entity) to be located
        :return: FileSystemNode - The file system node (entity)
        """
        if rf'{node.path}' == path:
            return node
        if hasattr(node, 'children'):
            # Get the first file path part from the list, leaving the remaining non-traversed file path parts
            next_path = path_parts[1]
            next_node = node.children.get(next_path)
            if not next_node:
                return None
            return self.find_descendant_node(next_node, path_parts[1:], path)
        return None
