import enum
import errno
import os
from pathlib import Path
from typing import List, Dict

from file_system_entities.entity_factory import FileSystemEntityFactory
from file_system_entities.entity_types_enum import EntityTypes
from helpers import file_path, recursive_size_update, MAIN_DRIVE
from file_system_entities.file_system_entities import FileSystemEntity, Drive, TextFile
from illegal_file_system_operation import IllegalFileSystemOperation
from not_a_text_file_error import NotATextFileError


class FileSystem:
    def __init__(self):
        """
        Initialize the File System instance
        """
        self.drives: Dict[str, FileSystemEntity] = {
            MAIN_DRIVE: Drive(EntityTypes.DRIVE, MAIN_DRIVE)
        }

    def create(self, type: enum.Enum, name: str, parent_path: str = None) -> FileSystemEntity:
        """
        Creates a file system node (entity)
        :param type: enum.Enum - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param parent_path: str - Path of the parent file system node (entity)
        :return: FileSystemEntity
        :raises FileNotFoundError, FileExistsError, IllegalFileSystemOperation
        """
        parent_node = self.find_node_by_path(parent_path)

        # If the parent path doesn't exist
        if not parent_node:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), parent_path)
        # If object to be created already exists
        if hasattr(parent_node, 'children') and parent_node.children.get(name):
            raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), file_path(parent_node.path, name))

        new_entity = FileSystemEntityFactory.for_type(type)(type, name, parent_node)
        if new_entity:
            self.insert_node(new_entity, parent_node)
            recursive_size_update(new_entity)
        return new_entity

    def delete(self, path: str) -> bool:
        """
        Deletes a file system node (entity)
        :param path: str - Path of the parent file system node (entity)
        :return: bool
        :raises FileNotFoundError, FileExistsError, IllegalFileSystemOperation
        """
        parent_path, name = self.get_parent_path_and_name(path)
        parent_node = self.find_node_by_path(parent_path)
        if parent_node and hasattr(parent_node, 'children'):
            if name in parent_node.children and parent_node.children[name]:
                del parent_node.children[name]
                recursive_size_update(parent_node)
                return True
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

    def move(self, source_path: str, dest_path: str) -> FileSystemEntity:
        """
        Move a file system node (entity) to a new path
        :param source_path: str - The source path where the file was located previously
        :param dest_path: str - The destination path where the file is to be moved to
        :return: FileSystemEntity - The new file system entity if moved successfully, else the old/current entity
        """
        # Get the destination parent path and the destination name
        dest_parent_path, dest_name = self.get_parent_path_and_name(dest_path)
        source_node = self.find_node_by_path(source_path)
        source_parent = source_node.parent
        dest_parent_node = self.find_node_by_path(dest_parent_path)

        if not self.valid_move_operation(dest_path, dest_name, dest_parent_node, source_path, source_node):
            return source_node

        new_entity = self.create(source_node.type, dest_name, dest_parent_path)
        if hasattr(source_node, 'children'):
            new_entity.children = source_node.children
        if hasattr(source_node, 'content'):
            new_entity.content = source_node.content

        recursive_size_update(new_entity)
        self.delete(source_path)
        recursive_size_update(source_parent)
        return new_entity

    def write_to_file(self, path: str, content: str) -> TextFile:
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
        path = Path(full_path)
        parent_path = path.parent
        name = path.parts[-1]
        return parent_path, name

    @staticmethod
    def valid_move_operation(dest_path, dest_name, dest_parent_node, source_path, source_node):
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

    @staticmethod
    def insert_node(entity: FileSystemEntity, parent_node: FileSystemEntity) -> None:
        """
        Insert a node entity as a child of parent_node
        :param entity: FileSystemEntity - The node entity to be inserted
        :param parent_node: FileSystemEntity - The node entity to receive a new child
        """
        if not hasattr(parent_node, 'children'):
            raise IllegalFileSystemOperation('Parent cannot contain any other entity')

        if entity.name in parent_node.children:
            raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), file_path(parent_node.path, entity.name))

        parent_node.add_child(entity)

    def find_node_by_path(self, path: str):
        """
        Find the parent node based on its file path
        :param path: str - The full path of the node (entity) to be located
        :return: FileSystemEntity - The file system node (entity)
        """
        if not path:
            return None
        path = Path(path)
        return self.find_descendant_node(self.drives[MAIN_DRIVE], path.parts, str(path))

    def find_descendant_node(self, node: FileSystemEntity, path_parts: List[str], path: str, current_index: int = 1):
        """
        Recursively traverse children of a file system node to find a given node by path
        :param node: FileSystemEntity - The file system node (entity) to be searched
        :param path_parts: List[str] - The list of path parts (found by splitting full path by the SEPARATOR)
        :param path: str - The full path of the node (entity) to be located
        :param current_index: int - the index of the path list in the current iteration
        :return: FileSystemEntity - The file system node (entity)
        """
        if node.path == path:
            return node
        if hasattr(node, 'children'):
            # Get the first file path part from the list, leaving the remaining non-traversed file path parts
            path_obj = Path(path)
            current_iteration_path = '/'.join(path_obj.parts[0:current_index + 1]).replace('//', '/')
            if current_iteration_path == node.path:
                current_index += 1

            # if path_obj.parts[current_index] == Path(node.path).parts[-1]:
            #     current_index += 1
            next_path = path_obj.parts[current_index]
            next_node = node.children.get(next_path)
            if not next_node:
                return None
            return self.find_descendant_node(next_node, path_parts[1:], path, current_index)
        return None
