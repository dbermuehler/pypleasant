from typing import Union, List

from pypleasant.artifacts import Database, Folder, Entry, Attachment


class PleasantElementNotFound(Exception):
    def __init__(self, complete_path: str, entry: str):
        super().__init__(f"Could not find {entry} in {complete_path}")


class PleasantEntryNotDistinct(Exception):
    def __init__(self, complete_path: str, entry: str):
        super().__init__(f"{entry} from {complete_path} exists in custom fields and attachments.")


class PathParser:
    def __init__(self, database: Database):
        self.database = database
        self._complete_path = None

    def lookup(self, path_as_str: str) -> Union[Folder, Entry, Attachment, str]:
        self._complete_path = path_as_str
        path = path_as_str.strip("/").split("/")
        return self.database if path == [''] else self._traverse_path(path, self.database)

    def _traverse_path(self, path: List[str], parent: Union[Database, Folder, Entry]) -> Union[
        Folder, Entry, Attachment, str]:
        if len(path) == 0:
            return parent
        elif isinstance(parent, Entry) and len(path) == 1:
            return self._get_entry_data(parent, path[0])
        else:
            child_name = path[0]
            if child_name not in parent:
                raise PleasantElementNotFound(self._complete_path, child_name)

            return self._traverse_path(path[1:], parent[child_name])

    def _get_entry_data(self, entry: Entry, data_name: str) -> Union[Attachment, str]:
        in_attachments = data_name in entry.attachments
        in_custom_fields = data_name in entry.custom_fields

        if in_attachments and in_custom_fields:
            raise PleasantEntryNotDistinct(self._complete_path, data_name)
        elif in_attachments:
            return entry.attachments[data_name]
        elif data_name in entry.custom_fields:
            return entry.custom_fields[data_name]
        else:
            raise PleasantElementNotFound(self._complete_path, data_name)
