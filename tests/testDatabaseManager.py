import unittest
from sources.Database.DatabaseManager import DatabaseManager
from sources.AeriesScraper import PeriodEncoder, Period


class TestDatabaseManager(unittest.TestCase):
    def testNewGradesEntry(self):
        testPeriod1 = Period(periodNum=1,
                            periodName="English",
                            teacherName="Donald",
                            gradePercent=98.3,
                            currentMark="A",
                            isPrior=False)
        testPeriod2 = Period(periodNum=2,
                            periodName="Algebra 1",
                            teacherName="Biden",
                            gradePercent=93.5,
                            currentMark="A-",
                            isPrior=False)
        dbManager = DatabaseManager()
        gradesJSON = dbManager._newUserGradesEntry(periods=[testPeriod1, testPeriod2])
        self.assertTrue(gradesJSON)
        self.assertTrue(gradesJSON[0])
        self.assertTrue(gradesJSON[1])

        period1 = gradesJSON[0]
        period2 = gradesJSON[1]
        self.assertEqual(period1['periodNum'], 1)
        self.assertEqual(period2['periodNum'], 2)
        self.assertEqual(period1['gradePercent'], 98.3)
        self.assertEqual(period2['currentMark'], "A-")

if __name__ == "__main__":
    unittest.main()
