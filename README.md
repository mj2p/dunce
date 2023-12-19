# Dunce
### Notes that have been marked down

---

Dunce is a simple note taking application.
Notes are stored in [Markdown](https://www.markdownguide.org/) files and backed up in a local git repo.

## Installation
Dunce needs python3 to be installed on your system (>3.10)
```bash
# clone the code repo
git clone https://github.com/mj2p/dunce.git
cd dunce
# setup and load a virtual environment
python3 -m venv ve
. ve/bin/activate
# install dependencies and build dunce
pip install .

# (optional) make dunce run from anywhere
sudo ln -sf $PWD/ve/bin/dunce /usr/local/bin/dunce

# run dunce
dunce
```

## Usage
When you run Dunce for the first time it will create a git repository in the data directory where notes are stored.
Notes are timestamped and stored in directories under the data directory, by `year/month/day`.

Write a note text in the input area at the bottom of the screen and hit the "Create" button. Dunce will display the note and save it to the data directory.

Each note will have some control buttons by which you can "View", "Edit" or "Delete" the note.

Whenever a note is Created, Edited or Deleted a commit is made to the git repo in the data directory.

The panel on the left of the screen allows you to show past notes split by the date they were created.
The search bar at the top will allow you to find notes based on a search term.

New notes are always added to today's date.

## Future work
- [ ] Allow the data directory to be configurable (you can set the `XDG_DATA_HOME` env var to set this currently).
- [ ] Allow the sensitivity of the search to be configurable.
- [ ] Allow config options for pushing changes to a remote git repo.
- [ ] Utilise the git repo to traverse history and recover deleted notes.
