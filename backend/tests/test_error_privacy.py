"""Public responses must not disclose upstream exceptions or filesystem paths."""
import unittest
from unittest.mock import patch
import server

MARKER = 'private-token-and-/srv/private/config'
SAFE_ERROR = 'Unable to complete the request. Please try again.'

class ErrorPrivacyTests(unittest.TestCase):
    def setUp(self):
        self.client = server.app.test_client()

    def test_service_failures_do_not_reach_public_responses(self):
        cases = [
            ('/api/search-location', {'query': 'London'}, server.geolocator, 'geocode', 500),
            ('/api/street-info', {'street_name': 'High Street'}, server, 'get_street_info', 500),
            ('/api/search-streets?q=High', None, server, 'search_streets_by_name', 500),
            ('/api/nearby-streets', {'latitude': 51, 'longitude': -1}, server.requests, 'post', 500),
            ('/api/nearby-streets-enhanced', {'lat': 51, 'lng': -1}, server.requests, 'post', 200),
            ('/api/street-info-enhanced', {'street_name': 'High Street'}, server, 'get_street_info', 200),
        ]
        for url, body, owner, name, status in cases:
            with self.subTest(url=url), patch.object(owner, name, side_effect=RuntimeError(MARKER)):
                response = self.client.get(url) if body is None else self.client.post(url, json=body)
                self.assertEqual(response.status_code, status)
                self.assertEqual(response.get_json()['error'], SAFE_ERROR)
                self.assertNotIn(MARKER, response.get_data(as_text=True))

    def test_legitimate_health_and_street_lookup_keep_response_shapes(self):
        self.assertEqual(self.client.get('/api/health').status_code, 200)
        info = {'name': 'High Street', 'origin': 'Historic shopping street'}
        with patch.object(server, 'get_street_info', return_value=info):
            response = self.client.post('/api/street-info', json={'street_name': 'High Street'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'success': True, 'street_info': info})

if __name__ == '__main__':
    unittest.main()
