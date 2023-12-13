from textual import on
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Markdown


class ViewNote(ModalScreen):
    CSS_PATH = "tcss/view_note.tcss"

    def compose(self) -> ComposeResult:
        self.note_title = Label(id="dunce-note-view-title")
        self.view_note = Markdown("", id="dunce-note-view-content")

        yield Container(
            self.note_title,
            VerticalScroll(self.view_note, id="dunce-note-view-scroll"),
            Container(
                Button("Close", variant="primary", id="dunce-note-view-close"), id="dunce-note-view-button-holder"
            ),
            id="dunce-view-note-grid",
        )

    @on(Button.Pressed, "#dunce-note-view-close")
    def close(self):
        self.app.pop_screen()
