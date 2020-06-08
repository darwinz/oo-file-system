from typing import Dict, List

from helpers import file_path


def calc_size(children: List, size: int = 0):
    """
    Calculate the size of the file system node (entity)
    :param children: List[FileSystemNode] - list of file system nodes to calculate the size recursively
    :param size: int - the size of all file system nodes in the list, calculated recursively
    :return: size: int
    """
    for child in children.values():
        size += child.size
    return size


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
        if None in [self.type, self.name, self.path, self.size]:
            raise Exception(f'Incorrect value passed')

    def set_size(self):
        raise NotImplementedError


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


class Drive(FileSystemNode, FSEntityContainerNode):
    def __init__(self, type: str, name: str):
        """
        Initialize a Drive instance
        :param type: int - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param parent: FileSystemNode - Parent file system node (entity)
        """
        FSEntityContainerNode.__init__(self)
        size = calc_size(self.children)
        super().__init__(type, name, name, size)

    def set_size(self) -> None:
        self.size = calc_size(self.children)


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
        size = calc_size(self.children)
        super().__init__(type, name, file_path(parent.path, name), size)

    def set_size(self) -> None:
        self.size = calc_size(self.children)


class TextFile(FileSystemNode, FSEntityContainableNode):
    def __init__(self, type: str, name: str, parent: FileSystemNode):
        """
        Initialize a TextFile instance
        :param type: int - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param parent: FileSystemNode - Parent file system node (entity)
        """
        FSEntityContainableNode.__init__(self, parent)
        super().__init__(type, name, file_path(parent.path, name), 0)

    def set_size(self) -> None:
        self.size = len(self.content)


class ZipFile(FileSystemNode, FSEntityContainerNode, FSEntityContainableNode):
    def __init__(self, type: str, name: str, parent: FileSystemNode):
        """
        Initialize a ZipFile instance
        :param type: int - The ID of the file system node type from the entity types enum
        :param name: str - The name of the file system node (entity)
        :param parent: FileSystemNode - Parent file system node (entity)
        """
        FSEntityContainerNode.__init__(self)
        FSEntityContainableNode.__init__(self, parent)
        size = int(round(calc_size(self.children) / 2))
        super().__init__(type, name, file_path(rf'{parent.path}', name), int(round(size)))

    def set_size(self) -> None:
        self.size = int(round(calc_size(self.children) / 2))
