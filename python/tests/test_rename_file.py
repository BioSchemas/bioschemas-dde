import unittest

from simplify_JSON import rename_file

class Test_rename_file(unittest.TestCase):
    def test_rename_file_1(self):
        """
        Test correct replacement of `.` with `-`
        """
        result = rename_file("ComputationalTool_v1.0-RELEASE.json")
        self.assertEqual(result, "ComputationalTool_v1-0-RELEASE.yml")

    def test_rename_file_2(self):
        """
        Test correct replacement of `.` with `-`
        """
        result = rename_file("Computational.Tool.json_v1.0-RELEASE.json")
        self.assertEqual(result, "Computational-Tool-json_v1-0-RELEASE.yml")

if __name__ == "__main__":
    unittest.main()
