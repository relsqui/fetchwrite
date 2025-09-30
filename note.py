class Note():
    def __init__(self, config, cursor, lines, date):
        self.cursor = cursor
        self.lines = lines
        self.date = date
        self.init_context(config)

    def init_context(self, config):
        self.before_mark, self.note_mark, self.after_mark = config[
            "note_mark_re"
        ].split(self.lines[self.cursor], maxsplit=1)
        self.before_offset = 0
        self.after_offset = 0
        while (
            len(self.before_context) < config["min_context_before"]
            and self.before_offset <= self.cursor
        ):
            self.before_offset += 1
        while len(self.after_context) < config[
            "min_context_after"
        ] and self.cursor + self.after_offset < len(self.lines):
            self.after_offset += 1

    @property
    def before_context(self):
        return (
            "\n".join(self.lines[self.cursor - self.before_offset : self.cursor])
            + "\n"
            + self.before_mark
        )

    @property
    def after_context(self):
        return (
            self.after_mark
            + "\n"
            + "\n".join(
                self.lines[self.cursor + 1 : self.cursor + self.after_offset + 1]
            )
        )

    @property
    def context(self):
        return (self.before_context + self.note_mark + self.after_context).strip()

    def add_before(self):
        if self.before_offset < self.cursor:
            self.before_offset += 1
            return True
        return False

    def add_after(self):
        if self.after_offset + self.cursor < len(self.lines) - 1:
            self.after_offset += 1
            return True
        return False

    def __str__(self):
        return (
            f"({self.date}) {getattr(self, "note", self.context.replace("\n", " / "))}"
        )
