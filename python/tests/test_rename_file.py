import unittest

from simplify_JSON import rename_file

class Test_rename_file(unittest.TestCase):
    def test_rename_file_comp_tool(self):
        """
        Test correct generation of file
        """
        result = rename_file("ComputationalTool", "1.0-RELEASE")
        self.assertEqual(result, "ComputationalTool/1.0-RELEASE.html")

    def test_rename_file_biosample(self):
        """
        Test correct generation of file
        """
        result = rename_file("BioSamples", "0.2-DRAFT")
        self.assertEqual(result, "BioSamples/0.2-DRAFT.html")

if __name__ == "__main__":
    unittest.main()
