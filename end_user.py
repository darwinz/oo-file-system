"""
This is a helper module that can assist with interaction with the File System
"""
import os

from file_system_entities.entity_types_enum import EntityTypes
from file_system import FileSystem, MAIN_DRIVE
from file_system_entities.file_system_entities import FileSystemEntity

file_system = FileSystem()


def pprint_tree(node: FileSystemEntity, file: str = None, _prefix: str = "", _last: bool = True):
    print(_prefix, "|- ", f"{node.name} ({node.size})", sep="", file=file)
    _prefix += "   " if _last else "|  "
    if hasattr(node, 'children'):
        child_count = len(node.children)
        for i, child in enumerate(node.children.values()):
            _last = i == (child_count - 1)
            pprint_tree(child, file, _prefix, _last)


if __name__ == "__main__":
    # Create a new folder
    folder = file_system.create(EntityTypes.FOLDER, 'my_folder', MAIN_DRIVE)
    folder2 = file_system.create(EntityTypes.FOLDER, 'my_folder2', MAIN_DRIVE)
    zip_file = file_system.create(EntityTypes.ZIP_FILE, 'my_zip', os.path.join(MAIN_DRIVE, 'my_folder'))
    print(f'Parent of zip_file => {zip_file.parent.name}')
    text_file = file_system.create(EntityTypes.TEXT_FILE, 'my_txt_file', os.path.join(MAIN_DRIVE, 'my_folder'))

    print('===============================')
    print('Printing the file system tree (with size)')
    pprint_tree(file_system.drives[MAIN_DRIVE])
    print('===============================')

    moved_file = file_system.move(text_file.path, os.path.join(MAIN_DRIVE, 'my_folder2', 'my_moved_txt_file'))

    print('===============================')
    print('File system tree (with size) after my_folder/my_txt_file moved to my_folder2/my_moved_txt_file')
    pprint_tree(file_system.drives[MAIN_DRIVE])
    print('===============================')

    text_file2 = file_system.create(EntityTypes.TEXT_FILE, 'my_txt_file2', os.path.join(MAIN_DRIVE, 'my_folder'))
    text_file3 = file_system.create(EntityTypes.TEXT_FILE, 'my_txt_file3', os.path.join(MAIN_DRIVE, 'my_folder',
                                                                                        'my_zip'))

    file_system.write_to_file(text_file2.path, 'This is the content of my file')
    file_system.write_to_file(text_file3.path, 'This is the content of my other file')
    file_system.write_to_file(moved_file.path, 'Content')

    print('===============================')
    print(f'The content of my_text_file2 => {text_file2.content}')
    print(f'The content of my_text_file3 => {text_file3.content}')
    print('===============================')
    print('===============================')
    print('File system tree (with size) after content added to two files')
    pprint_tree(file_system.drives[MAIN_DRIVE])
    print('===============================')
