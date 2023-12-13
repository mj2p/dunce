from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, TextArea


class DunceInput(Horizontal):
    class TextEntered(Message):
        def __init__(self, text: str, note_id: Optional[str] = None):
            self.text = text

            if note_id:
                # note_id used for editing
                self.note_id = note_id

            super().__init__()

    def compose(self) -> ComposeResult:
        self.text_area = TextArea(id="dunce-text-area", language="markdown", theme="vscode_dark")
        yield self.text_area
        self.enter_button = Button("Create", id="dunce-create", variant="success")
        yield self.enter_button
        self.save_button = Button("Save", id="dunce-edit-save", variant="primary")
        yield self.save_button

    @on(Button.Pressed, "#dunce-create")
    def enter_note(self):
        self.post_message(self.TextEntered(self.text_area.text))

    @on(Button.Pressed, "#dunce-edit-save")
    def edit_note(self):
        self.post_message(self.TextEntered(self.text_area.text, self.note_id))
