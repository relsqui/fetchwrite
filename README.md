# fetchwrite

Fetches dated files from a Freewrite sync in Dropbox, checks for "notes" marked with a sentinel string, and provides a minimal interactive interface for browsing and summarizing them.

Only processes file content in-memory; doesn't save anything.

(It's for reviewing journal entries for therapy notes before taking a video call on my work computer.)

## Usage

```sh
# if necessary:
# pipx install pipenv
pipenv install
pipenv run python main.py
```

## Configuration

- In main.py:
  - `dropbox_app_url` - the settings page of a Dropbox app with read access
  - `postbox_directory` - the path to the files you want to browse
- In notes.py:
  - `min_context_before` - how many characters to show before each note mark
  - `min_context_after` - the same but for after the mark
  - `note_marks` - a list of strings that identify part of a file as a note to review
