import enum
from typing import Dict

from helpers import file_path, calc_size


class FileSystemEntity:
    def __init__(self, type: enum.Enum, name: str, path: str, size: int):
        """
        :param type: enum.Enum - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param path: str - The concatenation of the names of the containing entities, from the drive
                down to and including the entity.  The names are separated by '\'
        :param size: int - An integer defined as follows:
                * For a text file - it is the length of its contents
                * For a drive or folder, it is the sum of all sizes of the entities it contains
                * For a zip file, it is one half of the sum of all sizes of the entities it contains
        """
        self.type: enum.Enum = type
        self.name: str = name
        self.path: str = path
        self.size: int = size

    def set_size(self):
        raise NotImplementedError


class ContainableMixin:
    def __init__(self, parent: FileSystemEntity):
        """
        A shared, inheritable class for file system nodes (entities) that can be contained by other nodes
        :param parent: FileSystemEntity - Parent file system node (entity)
        """
        self.parent: FileSystemEntity = parent


class ContainerMixin:
    def __init__(self):
        """
        A shared, inheritable class for file system nodes (entities) that can contain other nodes
        """
        self.children: Dict[str, FileSystemEntity] = {}

    def add_child(self, child: FileSystemEntity):
        """
        Add a child to the children list
        :param child: FileSystemEntity - the child node to be added
        """
        self.children[child.name] = child


class Drive(FileSystemEntity, ContainerMixin):
    def __init__(self, type: enum.Enum, name: str):
        """
        Initialize a Drive instance
        :param type: enum.Enum - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param parent: FileSystemEntity - Parent file system node (entity)
        """
        ContainerMixin.__init__(self)
        size = calc_size(self.children)
        super().__init__(type, name, name, size)

    def set_size(self) -> None:
        self.size = calc_size(self.children)


class Folder(FileSystemEntity, ContainerMixin, ContainableMixin):
    def __init__(self, type: enum.Enum, name: str, parent: FileSystemEntity):
        """
        Initialize a Folder instance
        :param type: enum.Enum - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param parent: FileSystemEntity - Parent file system node (entity)
        """
        ContainerMixin.__init__(self)
        ContainableMixin.__init__(self, parent)
        size = calc_size(self.children)
        super().__init__(type, name, file_path(parent.path, name), size)

    def set_size(self) -> None:
        self.size = calc_size(self.children)


class TextFile(FileSystemEntity, ContainableMixin):
    def __init__(self, type: enum.Enum, name: str, parent: FileSystemEntity, content: str = ''):
        """
        Initialize a TextFile instance
        :param type: enum.Enum - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param parent: FileSystemEntity - Parent file system node (entity)
        """
        ContainableMixin.__init__(self, parent)
        super().__init__(type, name, file_path(parent.path, name), 0)
        self.content = content

    def set_size(self) -> None:
        self.size = len(self.content)


class ZipFile(FileSystemEntity, ContainerMixin, ContainableMixin):
    def __init__(self, type: enum.Enum, name: str, parent: FileSystemEntity):
        """
        Initialize a ZipFile instance
        :param type: enum.Enum - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param parent: FileSystemEntity - Parent file system node (entity)
        """
        ContainerMixin.__init__(self)
        ContainableMixin.__init__(self, parent)
        size = int(round(calc_size(self.children) / 2))
        super().__init__(type, name, file_path(rf'{parent.path}', name), int(round(size)))

    def set_size(self) -> None:
        self.size = int(round(calc_size(self.children) / 2))
