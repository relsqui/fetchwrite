import dropbox
import re
from contextlib import closing
from datetime import datetime, timedelta, fromisoformat

# get a new one here https://www.dropbox.com/developers/apps/info/h74acmduf2e68vq
# TODO: auth that doesn't require replacing this regularly (oauth with refresh I guess)
token_file = ".access_token"
postbox_directory = "/Apps/Postbox/A/"
note_marks = ["(*)", "**"]
note_mark_re = re.compile(f"({"|".join(map(re.escape, note_marks))})")
min_context_before = 200 #characters
min_context_after = 50 #characters

def get_access_token():
  with open(token_file, "r") as f:
    return f.readline().rstrip()

def get_files_since(dbx, since_date):
  recent_files = []
  # if this starts to be too much for one page, see here for how to work with a cursor
  # https://dropbox-sdk-python.readthedocs.io/en/latest/api/dropbox.html#dropbox.dropbox_client.Dropbox.files_list_folder
  for entry in dbx.files_list_folder(postbox_directory).entries:
    # entry type: https://dropbox-sdk-python.readthedocs.io/en/latest/api/files.html#dropbox.files.FileMetadata
    if fromisoformat(entry.client_modified) > since_date:
      recent_files.append(entry)
  return recent_files

def get_file_lines(dbx, file):
  # _ is the metadata we already have
  # response is one of these: https://docs.python-requests.org/en/latest/api/#requests.Response
  _, response = dbx.files_download(postbox_directory + file.name)
  response.raise_for_status()
  with closing(response) as r:
    return r.content.decode("utf-8").splitlines()

def is_a_note(line):
  return note_mark_re.search(line) != None

def find_notes(file, lines):
  for cursor in range(len(lines)):
    line = lines[cursor]
    if not is_a_note(line):
      continue
    line_parts = note_mark_re.split(line, maxsplit=1)
    before_context = line_parts[0]
    note_mark = line_parts[1]
    after_context = line_parts[2]
    before_offset = 0
    while len(before_context) < min_context_before and cursor - before_offset >= 0:
      before_offset += 1
      before_context = lines[cursor - before_offset] + "\n" + before_context
    after_offset = 0
    while len(after_context) < min_context_after and cursor + after_offset < len(lines):
      after_offset += 1
      after_context += "\n" + lines[cursor + after_offset]
    print(file.client_modified)
    print(before_context + note_mark + after_context)
    input()

def main():
  dbx = dropbox.Dropbox(get_access_token())
  since_date = datetime.today() - timedelta(days=14)
  filenames = get_files_since(dbx, since_date)
  for file in filenames:
    lines = get_file_lines(dbx, file)
    find_notes(file, lines)

if __name__ == "__main__":
  main()
