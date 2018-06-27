import unittest
import unittest.mock as mock

import mycity.test.test_constants as test_constants
import mycity.test.unit_tests.base as base
import mycity.utilities.google_maps_utils as g_maps_utils


class TestGoogleMapsUtilities(base.BaseTestCase):

    def test_combine_driving_data_with_destinations(self):
        location_type = 'FAKE'
        closest_location_info = {'destination_addresses': 
                                 ['1000 Dorchester Ave, Boston, MA 02125, USA', 
                                  '94 Sawyer Ave, Dorchester, MA 02125, USA'], 
                                 'origin_addresses': ['46 Everdean St, Dorchester, MA 02122, USA'], 
                                 'rows': [{'elements': 
                                           [{'distance': {'text': '1.4 mi', 'value': 2207}, 
                                             'duration': {'text': '7 mins', 'value': 397},
                                             'status': 'OK'}, 
                                            {'distance': {'text': '1.5 mi', 'value': 2458}, 
                                             'duration': {'text': '7 mins', 'value': 425}, 
                                             'status': 'OK'}]}], 'status': 'OK'}
        dests = ['1000 Dorchester Ave Boston, MA', '94 Sawyer Ave Boston, MA']
        to_test = g_maps_utils.combine_driving_data_with_destinations(closest_location_info,
                                                                      location_type,
                                                                      dests)
        self.assertIn(g_maps_utils.DRIVING_DISTANCE_TEXT_KEY, to_test[0])
        self.assertIn(g_maps_utils.DRIVING_TIME_TEXT_KEY, to_test[0])
        self.assertIn(location_type, to_test[0])

    def test_setup_google_maps_query_params(self):
        origin = "46 Everdean St Boston, MA"
        dests = ["123 Fake St Boston, MA", "1600 Penn Ave Washington, DC"]
        to_test = g_maps_utils._setup_google_maps_query_params(origin, dests)
        self.assertEqual(origin, to_test["origins"])
        self.assertEqual(dests, to_test["destinations"].split("|"))
        self.assertEqual("imperial", to_test["units"])

    @unittest.skipUnless(test_constants.HAS_INTERNET_CONNECTION, 
                         "no connection to Internet")
    def test_get_driving_info(self):
        origin = "46 Everdean St Boston, MA"
        location_type = "FAKE"
        dests = ["1000 Dorchester Ave Boston, MA", "94 Sawyer Ave Boston, MA"]
        to_test = g_maps_utils._get_driving_info(origin, location_type, dests)
        expected = [{'Driving distance': 2207, 'Driving distance text': '1.4 mi', 
                     'Driving time': 399, 'Driving time text': '7 mins', 
                     'FAKE': '1000 Dorchester Ave Boston, MA'}, 
                    {'Driving distance': 2458, 'Driving distance text': '1.5 mi',
                     'Driving time': 427, 'Driving time text': '7 mins', 
                     'FAKE': '94 Sawyer Ave Boston, MA'}]
        self.assertEqual(to_test, expected)
