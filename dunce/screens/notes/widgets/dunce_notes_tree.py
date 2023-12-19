import os
import time
from pathlib import Path
from typing import List

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Input, Tree
from textual.widgets._tree import TreeNode
from thefuzz import process

from dunce.utils import NOTES_DIR


class DunceNotesTree(Vertical):
    class DunceNodeSelected(Message):
        def __init__(self, node: TreeNode):
            self.node = node
            super().__init__()

    class DunceSearch(Message):
        def __init__(self, search_term: str, results: List, start_time: float):
            self.search_term = search_term
            self.results = results
            self.start_time = start_time
            super().__init__()

    def compose(self) -> ComposeResult:
        self.input = Input(placeholder="Search notes", id="dunce-search-input")
        yield self.input
        self.dunce_tree = Tree("notes", id="dunce-tree")
        yield self.dunce_tree

    async def on_mount(self):
        await self.populate_tree()
        self.dunce_tree.show_guides = False

    async def populate_tree(self):
        self.dunce_tree.reset("notes")
        self.dunce_tree.root.expand()

        notes = []

        for root, dirs, files in os.walk(NOTES_DIR):
            if files:
                if ".git" in root:
                    continue

                notes.append(os.path.relpath(root, NOTES_DIR))

        for note in sorted(notes):
            self.dunce_tree.root.add_leaf(note)

    def on_tree_node_selected(self, event: Tree.NodeSelected):
        self.post_message(self.DunceNodeSelected(event.node))

    @on(Input.Submitted, "#dunce-search-input")
    async def search(self, message: Input.Submitted):
        start_time = time.monotonic()
        search_term = message.value
        search_data = []

        for root, dirs, files in os.walk(NOTES_DIR):
            for file in files:
                if ".git" in root:
                    continue

                search_data.append(f"{Path(root, file).read_text()}|||{Path(root, file)}")

        results = process.extract(search_term, search_data)
        filtered_results = []

        for result in sorted(results, key=lambda x: x[1]):
            if result[1] >= 45:
                filtered_results.append(result[0].split("|||")[1])

        self.post_message(self.DunceSearch(search_term=search_term, results=filtered_results, start_time=start_time))
