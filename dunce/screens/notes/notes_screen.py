import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from git import Repo
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header

from dunce.utils import NOTES_DIR

from .widgets.dunce_input import DunceInput
from .widgets.dunce_markdown_viewer import DunceMarkdownViewer, DunceNote
from .widgets.dunce_notes_tree import DunceNotesTree


class NotesScreen(Screen):
    CSS_PATH = "tcss/notes.tcss"

    async def action_undo(self) -> None:
        if not hasattr(self, "repo"):
            return

        commits = list(self.repo.iter_commits("master", max_count=2))

        if len(commits) < 2:
            self.notify(message="At beginning of history")
            return

        self.repo.head.reset("HEAD~1", index=True, working_tree=True)
        await self.load_notes(datetime.now())
        self.notify(message=f'Reset to "{commits[0].message}"')

    async def render_day_notes(self, date: Optional[datetime] = None):
        if date is None:
            date = datetime.now()

        self.notes_path = Path(NOTES_DIR, str(date.year), str(date.month), str(date.day))
        self.notes_path.mkdir(parents=True, exist_ok=True)

        self.markdown.title.update(f"Dunce Notes {date.day}/{date.month}/{date.year}")

        notes = []

        for note_f in self.notes_path.iterdir():
            if note_f.suffix != ".md":
                continue

            notes.append(note_f)

        self.notes = []

        for note_f in sorted(notes):
            self.notes.append(note_f)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        self.dunce_tree = DunceNotesTree(id="dunce-notes-tree")
        yield self.dunce_tree
        self.markdown = DunceMarkdownViewer(id="dunce-markdown")
        self.input = DunceInput(id="dunce-input")
        yield Vertical(self.markdown, self.input, id="dunce-notes")

    async def on_mount(self):
        if not Path(NOTES_DIR, ".git").exists():
            self.repo = Repo.init(NOTES_DIR)
        else:
            self.repo = Repo(NOTES_DIR)

        await self.load_notes(datetime.now())

    async def load_notes(self, timestamp: datetime):
        for node in self.dunce_tree.dunce_tree.root.children:
            if str(node.label) == f"{timestamp.year}/{timestamp.month}/{timestamp.day}":
                self.dunce_tree.dunce_tree.select_node(node)

        await self.render_day_notes(timestamp)
        self.markdown.note_container.remove_children()
        await self.markdown.note_container.set_loading(True)

        for note_f in self.notes:
            timestamp = datetime.fromisoformat(note_f.stem)
            note_id = await self.generate_note_id(timestamp)
            await self.markdown.add_note(note_id, timestamp.isoformat(), note_f.read_text())

        await self.markdown.note_container.set_loading(False)

        self.input.text_area.focus()

    @staticmethod
    async def generate_note_id(ts: datetime) -> str:
        return (
            f'dunce-{ts.strftime("%Y")}{ts.strftime("%m")}{ts.strftime("%d")}'
            f'{ts.strftime("%H")}{ts.strftime("%M")}{ts.strftime("%S")}'
        )

    @staticmethod
    async def parse_note_id(note_id: str) -> Path:
        date_time_string = note_id.replace("dunce-", "")
        date_time = datetime.strptime(date_time_string, "%Y%m%d%H%M%S")
        return Path(
            NOTES_DIR,
            f"{date_time.year}",
            f"{date_time.month}",
            f"{date_time.day}",
            f'{date_time.isoformat(timespec="seconds")}.md',
        )

    async def create_new_note(self, message: DunceInput.TextEntered) -> None:
        note_date = datetime.now()
        new_note = message.text.replace("\n", "  \n")

        new_note_path = Path(
            NOTES_DIR,
            f"{note_date.year}",
            f"{note_date.month}",
            f"{note_date.day}",
            f'{note_date.isoformat(timespec="seconds")}.md',
        )

        new_note_path.parent.mkdir(parents=True, exist_ok=True)
        new_note_path.write_text(new_note)

        self.input.text_area.clear()
        await self.load_notes(note_date)
        await self.dunce_tree.populate_tree()
        self.repo.index.add([new_note_path.relative_to(NOTES_DIR)])
        self.repo.index.commit(f"Add {new_note_path}")
        self.notify(message=f"Added {new_note_path.stem}")

    async def edit_note(self, message: DunceInput.TextEntered) -> None:
        updated_note = message.text.replace("\n", "  \n")
        note_path = await self.parse_note_id(message.note_id)
        note_path.write_text(updated_note)

        self.input.text_area.clear()
        note_widget = self.markdown.note_container.query_one(f"#{message.note_id}")
        await note_widget.note.update(updated_note)
        self.input.enter_button.display = "block"
        self.input.save_button.display = "none"
        await self.dunce_tree.populate_tree()
        self.repo.index.add([note_path.relative_to(NOTES_DIR)])
        self.repo.index.commit(f"Edit {note_path}")
        self.notify(message=f"Saved {note_path.stem}")

    async def on_dunce_input_text_entered(self, message: DunceInput.TextEntered) -> None:
        """
        Text has been submitted. Determine if we are adding or editing and act accordingly
        """
        if not message.text:
            return

        if hasattr(message, "note_id"):
            # note id is set if we are editing an existing note
            await self.edit_note(message)
        else:
            await self.create_new_note(message)

    async def on_dunce_notes_tree_dunce_node_selected(self, message: DunceNotesTree.DunceNodeSelected):
        """
        Node (date) selected in the side bar
        We should show the notes from that date
        """
        try:
            notes_date = datetime.strptime(str(message.node.label), "%Y/%m/%d")
        except ValueError:
            return

        self.input.text_area.clear()
        await self.load_notes(notes_date)

    async def on_dunce_notes_tree_dunce_search(self, message: DunceNotesTree.DunceSearch):
        self.markdown.note_container.remove_children()
        self.markdown.title.update(
            f"Found {len(message.results)} notes matching '{message.search_term}' "
            f"in {round(time.monotonic() - message.start_time, 4)} seconds"
        )

        for note_path in message.results:
            note_f = Path(note_path)
            timestamp = datetime.fromisoformat(note_f.stem)
            note_id = await self.generate_note_id(timestamp)
            await self.markdown.add_note(note_id, note_f.stem, note_f.read_text(), scroll=False)

        self.dunce_tree.input.clear()

    async def on_dunce_note_edit_note(self, message: DunceNote.EditNote):
        note_path = await self.parse_note_id(message.note_id)
        note_contents = note_path.read_text()
        self.input.text_area.text = note_contents
        # configure the UI for editing
        self.input.note_id = message.note_id
        self.input.enter_button.display = "none"
        self.input.save_button.display = "block"
        await self.dunce_tree.populate_tree()
        self.input.text_area.focus()

    async def on_dunce_note_delete_note(self, message: DunceNote.EditNote):
        note_path = await self.parse_note_id(message.note_id)
        note_path.unlink()
        note_widget = self.markdown.note_container.query_one(f"#{message.note_id}")
        await note_widget.remove()
        await self.dunce_tree.populate_tree()
        self.repo.index.remove([str(note_path.relative_to(NOTES_DIR))])
        self.repo.index.commit(f"Delete {note_path}")
        self.notify(message=f"Deleted {note_path.stem}")
