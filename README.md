# fetchwrite

Fetches dated files from a Freewrite sync in Dropbox, searches for "notes" marked with a sentinel string, and provides a minimal interactive interface for browsing and summarizing them.

Only processes file content in-memory; doesn't save anything.

(It's for reviewing journal entries for therapy notes before having a remote appointment on my work computer.)

## Setup
- [Create a Dropbox app](https://www.dropbox.com/developers/apps) with `files.content.read` permission
- Rename `config.toml.example` to `config.toml`
- Add the "App key" from your app settings page to `config.toml`
- Update other configuration values if you want to

```sh
# if necessary:
# pipx install pipenv
pipenv install
```

## Usage

```sh
pipenv run python main.py
```
