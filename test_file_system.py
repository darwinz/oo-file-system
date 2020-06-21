import os
import unittest

from entity_types_enum import EntityTypes
from file_system import FileSystem
from helpers import MAIN_DRIVE


class TestFileSystem(unittest.TestCase):
    def setUp(self):
        self.file_system = FileSystem()
        drive = self.file_system.get_root_node()
        self.test_folder = self.file_system.create(EntityTypes.FOLDER, 'test_folder', drive.path)
        self.test_folder2 = self.file_system.create(EntityTypes.FOLDER, 'test_folder2', drive.path)
        self.text_file1 = self.file_system.create(EntityTypes.TEXT_FILE, 'text_file1', self.test_folder.path)
        self.text_file2 = self.file_system.create(EntityTypes.TEXT_FILE, 'text_file2', self.test_folder.path)
        self.text_file3 = self.file_system.create(EntityTypes.TEXT_FILE, 'text_file3', self.test_folder2.path)
        self.zip_file1 = self.file_system.create(EntityTypes.ZIP_FILE, 'zip_file1', self.test_folder2.path)
        self.text_file4 = self.file_system.create(EntityTypes.TEXT_FILE, 'text_file4', self.zip_file1.path)

    def test_create_should_create_folder(self):
        type = EntityTypes.FOLDER
        name = 'testfolder'
        parent = self.test_folder
        created = self.file_system.create(type, name, parent.path)
        self.assertIn(created.name, parent.children)

    def test_create_should_create_file(self):
        type = EntityTypes.TEXT_FILE
        name = 'testfile'
        parent = self.test_folder
        created = self.file_system.create(type, name, parent.path)
        self.assertIn(created.name, parent.children)

    def test_create_should_not_allow_duplicate(self):
        type = EntityTypes.FOLDER
        name = 'test_folder'
        parent = self.file_system.get_root_node()
        with self.assertRaises(FileExistsError):
            self.file_system.create(type, name, parent.path)

    def test_create_should_not_allow_if_no_parent(self):
        type = EntityTypes.ZIP_FILE
        name = 'test'
        with self.assertRaises(FileNotFoundError):
            self.file_system.create(type, name, os.path.join(MAIN_DRIVE, 'cant_find_me'))

    def test_delete_should_delete_file(self):
        type = EntityTypes.TEXT_FILE
        name = 'testfile1'
        parent = self.test_folder
        created = self.file_system.create(type, name, parent.path)
        self.file_system.delete(created.path)
        self.assertNotIn(created.name, parent.children)

    def test_delete_should_error_if_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.file_system.delete(os.path.join(MAIN_DRIVE, 'i_dont_exist'))

    def test_move_should_move_file(self):
        type = EntityTypes.TEXT_FILE
        name = 'test_pre_move_file'
        moved_name = 'test_moved_file'
        parent = self.test_folder
        moved_parent = self.test_folder2
        created = self.file_system.create(type, name, parent.path)
        moved = self.file_system.move(created.path, os.path.join(moved_parent.path, moved_name))
        self.assertNotIn(created.name, parent.children)
        self.assertIn(moved.name, moved_parent.children)

    def test_write_to_file_should_change_content(self):
        content = 'Test Content'
        self.file_system.write_to_file(self.text_file1.path, content)
        self.assertEqual(content, self.text_file1.content)

    def test_write_to_file_should_change_size(self):
        content = 'More Test Content'
        expected_size = len(content)
        self.file_system.write_to_file(self.text_file2.path, content)
        self.assertEqual(expected_size, self.text_file2.size)

    def test_write_to_file_should_change_parent_size(self):
        content = 'More Test Content'
        expected_size = len(content)
        self.file_system.write_to_file(self.text_file3.path, content)
        self.assertEqual(expected_size, self.test_folder2.size)
        
    def test_write_to_file_in_zip_file_should_change_parent_size(self):
        content = 'File inside zip file content'
        # Zip file should expect to be half the size of the inner contents
        expected_size = len(content) / 2
        self.file_system.write_to_file(self.text_file4.path, content)
        self.assertEqual(expected_size, self.zip_file1.size)

