import enum

from file_system_entities.entity_types_enum import EntityTypes
from file_system_entities.file_system_entities import Folder, TextFile, ZipFile


class FileSystemEntityFactory:
    @staticmethod
    def for_type(entity_type: enum.Enum):
        types = {
            EntityTypes.FOLDER.value: Folder,
            EntityTypes.TEXT_FILE.value: TextFile,
            EntityTypes.ZIP_FILE.value: ZipFile
        }
        return types.get(entity_type.value)
