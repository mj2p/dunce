from textual.app import App

from .screens.notes.notes_screen import NotesScreen
from .screens.notes.view_note_modal import ViewNote
from .screens.notes.widgets.dunce_markdown_viewer import DunceNote


class DunceApp(App):
    TITLE = "Dunce"
    SUB_TITLE = "Notes that have been marked down"
    SCREENS = {"notes": NotesScreen()}

    def on_mount(self) -> None:
        self.push_screen("notes")

    async def on_dunce_note_view_note(self, message: DunceNote.ViewNote):
        note_path = await self.SCREENS["notes"].parse_note_id(message.note_id)
        view_note_screen = ViewNote()
        await self.push_screen(view_note_screen)
        view_note_screen.note_title.update(message.note_id)
        view_note_screen.view_note.update(note_path.read_text())


def dunce():
    app = DunceApp()
    app.run()
