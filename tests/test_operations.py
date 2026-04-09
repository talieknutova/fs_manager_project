import unittest
import os
import shutil
import tempfile
from fs_manager.core import operations

class TestOperations(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, 'w') as f:
            f.write("Hello World")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_copy_file(self):
        dest_file = os.path.join(self.test_dir, "copy.txt")
        operations.copy_file(self.test_file, dest_file)
        self.assertTrue(os.path.exists(dest_file))

    def test_delete_file(self):
        operations.delete_item(self.test_file)
        self.assertFalse(os.path.exists(self.test_file))

    def test_delete_directory(self):
        sub_dir = os.path.join(self.test_dir, "sub_dir")
        os.makedirs(sub_dir)
        operations.delete_item(sub_dir)
        self.assertFalse(os.path.exists(sub_dir))

    def test_count_files(self):
        # Создаем еще пару файлов
        with open(os.path.join(self.test_dir, "test2.txt"), 'w') as f: f.write("1")
        with open(os.path.join(self.test_dir, "test3.txt"), 'w') as f: f.write("2")
        count = operations.count_files(self.test_dir)
        self.assertEqual(count, 3)

    def test_search_files(self):
        with open(os.path.join(self.test_dir, "script.py"), 'w') as f: f.write("print('hi')")
        results = operations.search_files(self.test_dir, r"\.py$")
        self.assertEqual(len(results), 1)
        self.assertTrue("script.py" in results[0])

    def test_add_date(self):
        operations.add_date(self.test_file)
        files_after = os.listdir(self.test_dir)
        self.assertEqual(len(files_after), 1)
        self.assertTrue(files_after[0].endswith("_test.txt"))
        self.assertTrue(files_after[0][0].isdigit())

    def test_backup(self):
        archive_path = os.path.join(self.test_dir, "backup")
        operations.create_backup(self.test_file, archive_path)
        self.assertTrue(os.path.exists(archive_path + ".zip"))

if __name__ == '__main__':
    unittest.main()