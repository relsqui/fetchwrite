import dropbox
from contextlib import closing
from datetime import datetime, timedelta

# get a new one here https://www.dropbox.com/developers/apps/info/h74acmduf2e68vq
# TODO: auth that doesn't require replacing this regularly (oauth with refresh I guess)
token_file = ".access_token"
postbox_directory = "/Apps/Postbox/A/"

def get_access_token():
  with open(token_file, "r") as f:
    return f.readline().rstrip()

def get_files_since(dbx, date):
  recent_files = []
  # if this starts to be too much for one page, see here for how to work with a cursor
  # https://dropbox-sdk-python.readthedocs.io/en/latest/api/dropbox.html#dropbox.dropbox_client.Dropbox.files_list_folder
  for entry in dbx.files_list_folder(postbox_directory).entries:
    # entry type: https://dropbox-sdk-python.readthedocs.io/en/latest/api/files.html#dropbox.files.FileMetadata
    # relevant attributes: .id, .name, .client_modified
    # TODO: check .client_modified
    recent_files.append(entry)
  return recent_files

def get_file_lines(dbx, file):
  # _ is the metadata we already have
  # response is one of these: https://docs.python-requests.org/en/latest/api/#requests.Response
  _, response = dbx.files_download(postbox_directory + file.name)
  response.raise_for_status()
  with closing(response) as r:
    return r.content.decode("utf-8").splitlines()

def find_stars(file, lines):
  print(file.id, file.name, file.client_modified, len(lines))

def main():
  dbx = dropbox.Dropbox(get_access_token())
  date = datetime.today() - timedelta(days=14)
  filenames = get_files_since(dbx, date)
  for file in filenames:
    lines = get_file_lines(dbx, file)
    find_stars(file, lines)

if __name__ == "__main__":
  main()