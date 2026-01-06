import re
import sys
import tomllib
from contextlib import closing
from datetime import date, timedelta

import dropbox
import pyperclip
from note import Note


def load_config():
  default_config = {
    "postbox_directory": "/Apps/Postbox/A/",
    "lookback": 7,
    "note_marks": ["!!", "**"],
    "min_context_before": 200,
    "min_context_after": 50,
  }
  with open("config.toml", "rb") as f:
    file_config = tomllib.load(f)
  merged = default_config | file_config
  merged["note_mark_re"] = re.compile(f"({'|'.join(map(re.escape, merged['note_marks']))})")
  return merged


def init_dropbox(config):
  # TODO: auth that doesn't require replacing this regularly (oauth with refresh I guess)
  dropbox_app_base_url = "https://www.dropbox.com/developers/apps/info/"
  url = dropbox_app_base_url + config["dropbox_app_key"]
  print("Generate a dev access token here and copy it: " + url)
  input("Don't paste it. Just hit enter once you've copied it.")
  access_token = pyperclip.paste().strip()
  dbx = dropbox.Dropbox(access_token)
  try:
    user = dbx.users_get_current_account()
  except Exception as e:
    print(f"Couldn't auth to Dropbox. :( Here's what I know:\n  {e}\nDouble-check your token?")
    sys.exit(1)
  else:
    print(f"Authed to Dropbox. Hi, {user.name.familiar_name}.")
  return dbx


def get_since_date(config):
  default_since = date.today() - timedelta(days=config["lookback"])
  while True:
    date_string = input(f"Check files since? ({default_since}) ")
    if len(date_string) == 0:
      return default_since
    try:
      return date.fromisoformat(date_string)
    except ValueError:
      print("Didn't understand that. Try YYYY-MM-DD or hit enter to accept the default.")


def date_string_from_filename(filename):
  # Freewrite saves files starting with an iso date
  # and ending with .txt
  return filename[:-4].split(" ", maxsplit=1)[0]


def get_files_since(config, dbx, since_date):
  recent_files = []
  # TODO: paging
  for entry in dbx.files_list_folder(config["postbox_directory"]).entries:
    if date.fromisoformat(date_string_from_filename(entry.name)) > since_date:
      recent_files.append(entry)
  return recent_files


def get_file_lines(config, dbx, file):
  _, response = dbx.files_download(config["postbox_directory"] + file.name)
  response.raise_for_status()
  with closing(response) as r:
    return r.content.decode("utf-8").splitlines()


def adjust_note(note):
  while True:
    print()
    print(note.context)
    command = input(f"\n({note.date}) Add context (b)efore or (a)fter, make (n)ote, (s)kip> ") or "?"
    match command[0]:
      case "b":
        if not note.add_before():
          print("This is the beginning of the file.")
      case "a":
        if not note.add_after():
          print("This is the end of the file.")
      case "n":
        note.note = command[1:].strip()
        return True
      case "s":
        return False
      case _:
        print("Type b, a, n <note>, or s.")


def find_notes(config, file, lines):
  notes = []
  for cursor, line in enumerate(lines):
    if config["note_mark_re"].search(line) is None:
      continue
    note = Note(config, cursor, lines, date_string_from_filename(file.name))
    if adjust_note(note):
      notes.append(note)
  return notes


def s(i):
  return "" if i == 1 else "s"


def main():
  config = load_config()
  dbx = init_dropbox(config)
  since_date = get_since_date(config)
  files = get_files_since(config, dbx, since_date)
  print(f"\nChecking files since {since_date}. Found {len(files)} file{s(len(files))}.")
  files.sort(key=lambda f: f.name)
  notes = []
  for file in files:
    lines = get_file_lines(config, dbx, file)
    notes.extend(find_notes(config, file, lines))
  print()
  for note in notes:
    print(f"- {note}")
  print()


if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    print()
