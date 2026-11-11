# SPDX-License-Identifier: MIT
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validator', ROOT / 'scripts/validate_catalog.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {
            'format': 'grandleon-campaign-catalog', 'formatVersion': 1,
            'id': 'example.campaigns', 'title': 'Example campaigns',
            'campaigns': [{
                'id': 'example', 'title': 'Example', 'description': 'A campaign.',
                'author': 'An author', 'version': '1.0.0', 'campaign': 'example',
                'playerMode': 'choice', 'languages': ['en', 'pt-BR'],
                'minimumPlayerVersion': '0.5.0',
                'assets': {'kind': 'builtin', 'pack': 'grandleon-core', 'version': 1},
                'package': {'url': 'https://example.invalid/example.gpk',
                            'sizeBytes': 10, 'sha256': 'a' * 64},
            }],
        }

    def test_valid_and_empty_catalogues(self):
        self.assertEqual(validator.validate(self.catalog), [])
        self.catalog['campaigns'] = []
        self.assertEqual(validator.validate(self.catalog), [])

    def test_invalid_entries(self):
        changes = [
            ('id', '../escape'), ('version', 'latest'), ('playerMode', 'three'),
            ('minimumPlayerVersion', 'tomorrow'), ('languages', []),
            ('assets', {'kind': 'builtin'}),
            ('package', {'url': 'http://example.invalid/x', 'sizeBytes': 10, 'sha256': 'a' * 64}),
            ('package', {'url': 'https://user:secret@example.invalid/x', 'sizeBytes': 10, 'sha256': 'a' * 64}),
            ('package', {'url': 'https://example.invalid/x', 'sizeBytes': 0, 'sha256': 'bad'}),
            ('package', {'url': 'https://example.invalid/x', 'sizeBytes': 16777217, 'sha256': 'a' * 64}),
        ]
        for key, value in changes:
            with self.subTest(field=key, value=value):
                catalog = copy.deepcopy(self.catalog)
                catalog['campaigns'][0][key] = value
                self.assertTrue(validator.validate(catalog))

    def test_duplicate_ids_and_unsupported_catalogue_version(self):
        self.catalog['campaigns'].append(copy.deepcopy(self.catalog['campaigns'][0]))
        self.assertTrue(validator.validate(self.catalog))
        self.catalog['campaigns'] = []
        self.catalog['formatVersion'] = 2
        self.assertTrue(validator.validate(self.catalog))

    def test_canonical_player_modes(self):
        for mode in ['one', 'two', 'choice']:
            self.catalog['campaigns'][0]['playerMode'] = mode
            self.assertEqual(validator.validate(self.catalog), [])
        for mode in ['solo', 'coop']:
            self.catalog['campaigns'][0]['playerMode'] = mode
            self.assertTrue(validator.validate(self.catalog))

    def test_player_supported_bounds(self):
        entry = self.catalog['campaigns'][0]
        entry['id'] = 'x' * 65
        self.assertTrue(validator.validate(self.catalog))
        entry['id'] = 'valid'
        entry['version'] = '01.0.0'
        self.assertTrue(validator.validate(self.catalog))
        entry['version'] = '1.0.0'
        entry['title'] = 'x' * 161
        self.assertTrue(validator.validate(self.catalog))

    def test_future_asset_kinds_are_representable(self):
        self.catalog['campaigns'][0]['assets'] = {'kind': 'bundle', 'manifestUrl': 'https://example.invalid/assets.json'}
        self.assertEqual(validator.validate(self.catalog), [])
        # A schema describes future requirements; current players must still
        # explicitly reject asset kinds they cannot install.


if __name__ == '__main__':
    unittest.main()
