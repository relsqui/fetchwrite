import dropbox
from contextlib import closing
from datetime import datetime, timedelta
from note import Note, is_a_note

# get a new one here https://www.dropbox.com/developers/apps/info/h74acmduf2e68vq
# TODO: auth that doesn't require replacing this regularly (oauth with refresh I guess)
token_file = ".access_token"
postbox_directory = "/Apps/Postbox/A/"

def get_access_token():
  with open(token_file, "r") as f:
    return f.readline().rstrip()

def get_files_since(dbx, since_date):
  recent_files = []
  # if this starts to be too much for one page, see here for how to work with a cursor
  # https://dropbox-sdk-python.readthedocs.io/en/latest/api/dropbox.html#dropbox.dropbox_client.Dropbox.files_list_folder
  for entry in dbx.files_list_folder(postbox_directory).entries:
    # entry type: https://dropbox-sdk-python.readthedocs.io/en/latest/api/files.html#dropbox.files.FileMetadata
    if entry.client_modified > since_date:
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
    command = input(f"\n({note.date}) add context (b)efore or (a)fter, make (n)ote, (s)kip> ") or "?"
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
    note = Note(file, cursor, lines)
    if adjust_note(note):
      notes.append(note)
  return notes

def main():
  dbx = dropbox.Dropbox(get_access_token())
  since_date = datetime.today() - timedelta(days=14)
  files = get_files_since(dbx, since_date)[:1]
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
  main()
