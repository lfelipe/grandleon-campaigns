# Grandleon campaigns

Campaigns for the [Grandleon tactical RPG player](https://github.com/lfelipe/grandleon).
The campaign browser is being developed for Grandleon 0.6; it is not included
in the published 0.5 application yet.

The player reads [catalog.json](catalog.json) to list available campaigns,
then downloads a package from this repository's Releases. Installed campaigns
remain playable offline. A GitHub account is not required.

## Playing

Open **Browse Campaigns** in a compatible Grandleon player. This is its default
catalogue. Choose a campaign, download it, then play with its supported player
count and language. Check the version requirements shown by the player.

The catalogue URL is:

```text
https://raw.githubusercontent.com/lfelipe/grandleon-campaigns/main/catalog.json
```

The first campaigns use the artwork and audio included with Grandleon. Custom
asset downloads are not implemented yet. The manifest records asset requirements
explicitly so future packages can introduce them without silently using the
wrong artwork.

## Sharing a campaign

1. Create your campaign in Grandleon. Keep an editable project export as a backup.
2. For the initial format, export a standalone game and use its `project/game.gpk`
   file as the playable package. Use the built-in artwork and audio.
3. Publish that file as a versioned GitHub Release asset. Add its title,
   description, author, version, languages, player mode, requirements, download
   URL, byte size and SHA-256 to your catalogue.
4. To appear here, submit a pull request with the catalogue entry and editable
   source under `campaigns/`. Maintainers review and publish the package.

You can also maintain your own public catalogue repository. Follow the same
[catalogue format](catalog.schema.json), use your own catalogue ID, and give
players its raw HTTPS JSON URL to add in **Browse Campaigns**. Campaign packages
can live in your own repository's Releases. Publishing here is optional.

Campaign IDs should stay stable across updates. Publish new versioned packages
and update the catalogue; preserve older release assets. The player checks
compatibility and checksums before installation. These checks detect damaged or
mismatched downloads; choose catalogue sources you trust.

Android is planned to support creating and exporting portable campaigns and
playing them on Android or PC. Exporting N64 ROMs and PS1 discs remains a PC
workflow, using the editable project export.

## Checking changes

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_catalog.py
python3 -m unittest discover -s tests
```

The schema is versioned separately from campaigns. The current player accepts
`formatVersion: 1` and the built-in `grandleon-core` asset pack, version `1`.
Unknown asset kinds can be described for future clients, but current players
must show them as unsupported rather than installing them with substituted assets.

Campaign source and this catalogue use the MIT license unless a campaign
explicitly states otherwise. Built-in art and audio ship with Grandleon and
retain their notices there; those assets are not copied into this repository.
