import unittest
import unittest.mock as unitmock

import os
from simplify_JSON import write_YAML_file

class Test_Write_YAML_file(unittest.TestCase):

    def test_write_YAML_file(self):
        """
        Test ability to write a YAML file
        """
        filename = 'OzWQr1VVB7.yml'
        assert not os.path.exists(filename), "File test.yml already exists and would be removed by this test."
        write_YAML_file({'A':'a', 'B':{'C':'c', 'D':'d', 'E':'e'}, 'F': [1,2,'3']}, filename)
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)

if __name__ == "__main__":
    unittest.main()
