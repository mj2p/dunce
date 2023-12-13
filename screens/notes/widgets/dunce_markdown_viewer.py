from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Label, Markdown, Static


class DunceNote(Horizontal):
    class ViewNote(Message):
        def __init__(self, note_id: str):
            self.note_id = note_id
            super().__init__()

    class EditNote(Message):
        def __init__(self, note_id: str):
            self.note_id = note_id
            super().__init__()

    class DeleteNote(Message):
        def __init__(self, note_id: str):
            self.note_id = note_id
            super().__init__()

    def compose(self):
        self.title = Label(classes="dunce-note-label")
        self.note = Markdown("", classes="dunce-note-contents")
        self.view_button = Button("View", variant="primary", classes="dunce-note-view")
        self.edit_button = Button("Edit", variant="default", classes="dunce-note-edit")
        self.delete_button = Button("Delete", variant="error", classes="dunce-note-delete")

        yield VerticalScroll(self.title, self.note, classes="dunce-note-scroller")

        yield VerticalScroll(self.view_button, self.edit_button, self.delete_button, classes="dunce-note-buttons")

    @on(Button.Pressed, ".dunce-note-view")
    def view_note(self):
        self.post_message(self.ViewNote(note_id=self.id))

    @on(Button.Pressed, ".dunce-note-edit")
    def edit_note(self):
        self.post_message(self.EditNote(note_id=self.id))

    @on(Button.Pressed, ".dunce-note-delete")
    def delete_note(self):
        self.post_message(self.DeleteNote(note_id=self.id))


class DunceMarkdownViewer(Static):
    def compose(self) -> ComposeResult:
        self.title = Label(id="dunce-notes-title")
        self.note_container = VerticalScroll(id="dunce-note-container")
        yield self.title
        yield self.note_container

    async def add_note(self, note_id: str, title: str, note: str, scroll: bool = True) -> None:
        new_note = DunceNote()
        await self.note_container.mount(new_note)
        new_note.title.update(title)
        new_note.id = note_id
        await new_note.note.update(note)

        if scroll:
            new_note.scroll_visible()
