import re

note_marks = ["(*)", "**"]
note_mark_re = re.compile(f"({"|".join(map(re.escape, note_marks))})")
min_context_before = 200 #characters
min_context_after = 50 #characters

def is_a_note(line):
  return note_mark_re.search(line) != None

class Note(object):
  def __init__(self, file, cursor, lines):
    self.file
    self.cursor = cursor
    self.lines = lines
    self.before_mark, self.note_mark, self.after_mark = note_mark_re.split(lines[cursor], maxsplit=1)
    self.before_offset = 0
    self.after_offset = 0
    self.init_context()

  def init_context(self):
    while len(self.before_context) < min_context_before and self.cursor - self.before_offset >= 0:
      self.before_offset += 1
    while len(self.after_context) < min_context_after and self.cursor + self.after_offset < len(self.lines):
      self.after_offset += 1

  @property
  def before_context(self):
    return "\n".join(self.lines[self.cursor-self.before_offset:self.cursor]) + "\n" + self.before_mark

  @property
  def after_context(self):
    return self.after_mark + "\n" + "\n".join(self.lines[self.cursor+1:self.cursor+self.after_offset+1])

  def __str__(self):
    return self.file.name + "\n" + (self.before_context + self.note_mark + self.after_context).strip()