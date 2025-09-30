import dropbox
import pyperclip
from contextlib import closing
from datetime import date, timedelta
from note import Note, is_a_note
from sys import exit

dropbox_app_url = "https://www.dropbox.com/developers/apps/info/h74acmduf2e68vq"
postbox_directory = "/Apps/Postbox/A/"

def init_dropbox():
  # TODO: auth that doesn't require replacing this regularly (oauth with refresh I guess)
  print("Generate a dev access token here and copy it: " + dropbox_app_url)
  input("Don't paste it. Just hit enter once you've copied it.")
  access_token = pyperclip.paste().strip()
  dbx = dropbox.Dropbox(access_token)
  try:
    user = dbx.users_get_current_account()
  except Exception as e:
    print(f"Couldn't auth to Dropbox. :( Here's what I know:\n  {e}\nDouble-check your token?")
    exit(1)
  else:
    print(f"Authed to Dropbox. Hi, {user.name.familiar_name}.")
  return dbx

def get_since_date():
  two_weeks_ago = date.today() - timedelta(days=15)
  while True:
    date_string = input(f"Check files since? ({two_weeks_ago}) ")
    if len(date_string) == 0:
      return two_weeks_ago
    try:
      return date.fromisoformat(date_string)
    except ValueError:
      print("Didn't understand that. Try YYYY-MM-DD or hit enter to accept the default.")

def date_string_from_filename(filename):
  # freewrite saves files starting with an iso date (and I fixed the one from before I set the time)
  return filename.split(" ", maxsplit=1)[0]

def get_files_since(dbx, since_date):
  recent_files = []
  # if this starts to be too much for one page, see here for how to work with a cursor
  # https://dropbox-sdk-python.readthedocs.io/en/latest/api/dropbox.html#dropbox.dropbox_client.Dropbox.files_list_folder
  for entry in dbx.files_list_folder(postbox_directory).entries:
    # entry type: https://dropbox-sdk-python.readthedocs.io/en/latest/api/files.html#dropbox.files.FileMetadata
    if date.fromisoformat(date_string_from_filename(entry.name)) > since_date:
      recent_files.append(entry)
  return recent_files

def get_file_lines(dbx, file):
  # _ is the metadata we already have
  # response is one of these: https://docs.python-requests.org/en/latest/api/#requests.Response
  _, response = dbx.files_download(postbox_directory + file.name)
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

def find_notes(file, lines):
  notes = []
  for cursor in range(len(lines)):
    line = lines[cursor]
    if not is_a_note(line):
      continue
    note = Note(cursor, lines, date_string_from_filename(file.name))
    if adjust_note(note):
      notes.append(note)
  return notes

def s(i):
  return "" if i == 1 else "s"

def main():
  dbx = init_dropbox()
  since_date = get_since_date() 
  files = get_files_since(dbx, since_date)
  print(f"\nChecking files since {since_date}. Found {len(files)} file{s(len(files))}.")
  files.sort(key=lambda f: f.name)
  notes = []
  for file in files:
    lines = get_file_lines(dbx, file)
    notes.extend(find_notes(file, lines))
  print()
  for note in notes:
    print(f"- {note}")
  print()

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    print()
