import unittest
from final_proj import *

# proj3_choc_test.py
# You must NOT change this file. You can comment stuff out while debugging but
# don't forget to restore it to its original form!

class TestDatabase(unittest.TestCase):

    def test_Countries_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Name FROM Countries'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Benin',), result_list)
        self.assertEqual(len(result_list), 57)

        sql = '''
            SELECT Name, Region, Population, Languages
            FROM Countries
            WHERE Name="Botswana"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        
        self.assertEqual(len(result_list), 1)
        self.assertEqual(result_list[0][0], "Botswana")
        self.assertEqual(result_list[0][1], "Africa")
        self.assertEqual(result_list[0][2], 2141206)
        self.assertEqual(result_list[0][3], "Setswana, English")

        conn.close()

    def test_Languages_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Language FROM Languages'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('French',), result_list)
        self.assertEqual(len(result_list), 38)

        sql = '''
            SELECT Language, SpokenIn, PastVolunteersSpeaking 
            FROM Languages
            WHERE Language="Arabic"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        
        self.assertEqual(len(result_list), 1)
        self.assertEqual(result_list[0][0], "Arabic")
        self.assertEqual(result_list[0][1], "Comoros, Jordan, Morocco, Tunisia")
        self.assertEqual(result_list[0][2], 7900)

        conn.close()

class TestClasses(unittest.TestCase):

    def test_CountryClass(self):

        test_data = countryfier()

        self.assertEqual(test_data[0].name, "Benin")
        self.assertEqual(test_data[0].region, "Africa")
        self.assertEqual(test_data[0].work_sectors, "Community Economic Development, Education, Environment, Health")
        
if __name__ == '__main__':
    unittest.main()