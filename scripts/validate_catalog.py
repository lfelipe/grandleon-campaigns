#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate a catalogue; optionally verify its public release downloads."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'catalog.schema.json').read_text(encoding='utf-8'))
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def validate(catalog):
    errors = [f"{'/'.join(map(str, error.absolute_path)) or 'catalog'}: {error.message}"
              for error in VALIDATOR.iter_errors(catalog)]
    if errors:
        return errors
    ids = set()
    for entry in catalog['campaigns']:
        if entry['id'] in ids:
            errors.append(f"duplicate campaign ID: {entry['id']}")
        ids.add(entry['id'])
        urls = [entry['package']['url']]
        if 'thumbnailUrl' in entry:
            urls.append(entry['thumbnailUrl'])
        for url in urls:
            parsed = urlparse(url)
            if not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
                errors.append(f"{entry['id']}: use a public HTTPS URL without credentials or a fragment")
    return errors


def verify_downloads(catalog):
    for entry in catalog['campaigns']:
        package = entry['package']
        request = Request(package['url'], headers={'User-Agent': 'Grandleon-Catalog-Validator/1'})
        digest = hashlib.sha256()
        size = 0
        with urlopen(request, timeout=30) as response:
            while chunk := response.read(65536):
                size += len(chunk)
                if size > package['sizeBytes']:
                    raise ValueError(f"{entry['id']}: download exceeds declared size")
                digest.update(chunk)
        if size != package['sizeBytes'] or digest.hexdigest() != package['sha256']:
            raise ValueError(f"{entry['id']}: download size or SHA-256 mismatch")
        print(f"Verified {entry['id']} {entry['version']} ({size} bytes)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalog', nargs='?', type=Path, default=ROOT / 'catalog.json')
    parser.add_argument('--verify-downloads', action='store_true')
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding='utf-8'))
        errors = validate(catalog)
        if errors:
            raise ValueError('\n'.join(errors))
        if args.verify_downloads:
            verify_downloads(catalog)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    print(f"Catalogue valid: {len(catalog['campaigns'])} campaign(s)")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
