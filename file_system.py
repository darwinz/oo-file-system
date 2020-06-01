import errno
import os
from datetime import datetime
from typing import List, Dict

from entity_types_enum import EntityTypes
from illegal_file_system_operation import IllegalFileSystemOperation

SEPARATOR = '\\'
file_path = lambda path, name: f'{path}{SEPARATOR}{name}'


class FileSystemNode:
    def __init__(self, type: int, name: str, path: str, size: int):
        """
        :param type: int - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param path: str - The concatenation of the names of the containing entities, from the drive
                down to and including the entity.  The names are separated by '\'
        :param size: int - An integer defined as follows:
                * For a text file - it is the length of its contents
                * For a drive or folder, it is the sum of all sizes of the entities it contains
                * For a zip file, it is one half of the sum of all sizes of the entities it contains
        """
        self.type: int = type if isinstance(type, int) else None
        self.name: str = name if isinstance(name, str) else None
        self.path: str = path if isinstance(path, str) else None
        self.size: int = size if isinstance(size, int) else None
        if not all([type, name, path, size]):
            raise Exception(f'Incorrect value passed')


class FSEntityContainableNode:
    def __init__(self, parent: FileSystemNode):
        """
        A shared, inheritable class for file system nodes (entities) that can be contained by other nodes
        :param parent: FileSystemNode - Parent file system node (entity)
        """
        self.parent: FileSystemNode = parent


class FSEntityContainerNode:
    def __init__(self):
        """
        A shared, inheritable class for file system nodes (entities) that can contain other nodes
        """
        self.children: Dict[str, FileSystemNode] = {}

    def add_child(self, child: FileSystemNode):
        """
        Add a child to the children list
        :param child: FileSystemNode - the child node to be added
        """
        self.children[child.name] = child

    def calc_size(self, children: List[FileSystemNode], size: int = 0):
        """
        Calculate the size of the file system node (entity)
        :param children: List[FileSystemNode] - list of file system nodes to calculate the size recursively
        :param size: int - the size of all file system nodes in the list, calculated recursively
        :return: size: int
        """
        for child in children:
            if hasattr(child, 'children'):
                size += self.calc_size(child.children, size)
            else:
                size += child.size
        return size


class Drive(FileSystemNode, FSEntityContainerNode):
    def __init__(self, type: str, name: str):
        """
        Initialize a Drive instance
        :param type: int - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param parent: FileSystemNode - Parent file system node (entity)
        """
        FSEntityContainerNode.__init__(self)
        size = self.calc_size(self.children)
        super().__init__(type, name, name, size)


class Folder(FileSystemNode, FSEntityContainerNode, FSEntityContainableNode):
    def __init__(self, type: str, name: str, parent: FileSystemNode):
        """
        Initialize a Folder instance
        :param type: int - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param parent: FileSystemNode - Parent file system node (entity)
        """
        FSEntityContainerNode.__init__(self)
        FSEntityContainableNode.__init__(self, parent)
        size = self.calc_size(self.children)
        super().__init__(type, name, file_path(parent.path, name), size)


class TextFile(FileSystemNode, FSEntityContainableNode):
    def __init__(self, type: str, name: str, parent: FileSystemNode, content: str):
        """
        Initialize a Folder instance
        :param type: int - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param parent: FileSystemNode - Parent file system node (entity)
        """
        FSEntityContainableNode.__init__(self, parent)
        self.content = content
        size = len(content)
        super().__init__(type, name, file_path(parent.path, name), size)


class ZipFile(FileSystemNode, FSEntityContainerNode, FSEntityContainableNode):
    def __init__(self, type: str, name: str, parent: FileSystemNode):
        """
        Initialize a Folder instance
        :param type: int - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param parent: FileSystemNode - Parent file system node (entity)
        """
        FSEntityContainerNode.__init__(self)
        FSEntityContainableNode.__init__(self, parent)
        size = self.calc_size(self.children) / 2
        super().__init__(type, name, file_path(parent.path, name), int(round(size)))


class FileSystem:
    def __init__(self):
        self.list_of_drives: Dict[str, FileSystemNode] = {}

    def find_parent_node(self, path: List[str]):
        



    def create(self, type: int, name: str, path: str) -> FileSystemNode:
        """
        Creates a file system node (entity)
        :param type: int - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param path: str - Path of the parent file system node (entity)
        :return: FileSystemNode
        """
        if not type or not name:
            raise ValueError('Type and name must be provided')

        # If the parent path doesn't exist
        if not os.path.exists(path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

        # If object to be created already exists
        if os.path.exists(file_path(path, name)):
            raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), file_path)

        if type == EntityTypes.DRIVE:
            self.list_of_drives[name] = Drive(type, name)
        elif type == EntityTypes.FOLDER:
            parent_node = self.find_parent_node(path)

    def delete(self, path: str) -> None:
        pass

    def move(self, source_path: str, dest_path: str) -> None:
        pass

    def write_to_file(self, path: str, content: str) -> None:
        pass
