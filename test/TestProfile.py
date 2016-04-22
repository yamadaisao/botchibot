import unittest
from entity import Profile

class TestProfile(unittest.TestCase):
    def setUp(self):
        #do something before testing each test method

    def tearDown(self):
        # do something after testing each test method

    def test_query(self):
        prof = Profile.all().fileter('mid =', '').get()
