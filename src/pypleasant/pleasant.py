from pypleasant.api import PleasantAPI
from pypleasant.artifacts import Database, Entry
from pypleasant.pathparser import PathParser


class NotAPleasantEntry(Exception):
    def __init__(self, path: str):
        super().__init__(f"{path} is not an entry")


class Pleasant:
    def __init__(self, url: str, user: str, password: str, verify_https: bool = True):
        self.api = PleasantAPI(url, user, password, verify_https)
        self.database = Database(self.api)

    def lookup_path(self, path: str) -> Entry:
        entry = PathParser(self.database).lookup(path)

        if not isinstance(entry, Entry):
            raise NotAPleasantEntry(path)
        else:
            return entry

    def lookup_entry_id(self, entry_id: str) -> Entry:
        return Entry(self.api.get_entry(entry_id), self.api)
