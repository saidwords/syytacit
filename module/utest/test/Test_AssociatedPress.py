import unittest
from module.associatedpress.lib.AssociatedPressWebService import AssociatedPressWebService
from module.associatedpress.model.AssociatedPressCategoryModel import AssociatedPressCategoryModel

class Test_AssociatedPress(unittest.TestCase):
    def setUp(self):
        foo=None
    def test_getBreakingNews(self):
        ap = AssociatedPressWebService()
        category = AssociatedPressCategoryModel()
        category.id=ap.CATEGORY_TOP_GENERAL_SHORT_HEADLINES
        headlines=ap.getBreakingNews(category)
        
    def test_parseDate(self):
        ap = AssociatedPressWebService()
        dateobj=ap.parseDate()
    def runTest(self):
        foo=None
    def tearDown(self):
        bar=None
