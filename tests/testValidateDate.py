import unittest
from app import validateDate

class TestValidateDate(unittest.TestCase):

    def testValidateDate(self):
        date = "2021-04-28T14:59:00Z"
        self.assertTrue(validateDate(dateString=date))

        date = "2020/04/28"
        self.assertFalse(validateDate(dateString=date))

if __name__ == "__main__":
    unittest.main()
