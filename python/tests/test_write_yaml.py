import unittest
import unittest.mock as unitmock

import os
from simplify_JSON import write_YAML_file

class Test_Write_YAML_file(unittest.TestCase):

    def test_write_YAML_file(self):
        """
        Test ability to write a YAML file
        """
        filename = 'test/OzWQr1VVB7.html'
        assert not os.path.exists(filename), "File test/OzWQr1VVB7.html already exists and would be removed by this test."
        write_YAML_file({'A':'a', 'B':{'C':'c', 'D':'d', 'E':'e'}, 'F': [1,2,'3']}, filename)
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)

if __name__ == "__main__":
    unittest.main()
