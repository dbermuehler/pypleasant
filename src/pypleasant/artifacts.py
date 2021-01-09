import base64
import pathlib
from collections import UserDict

from pypleasant.api import PleasantAPI


class Attachment:
    def __init__(self, attachment_as_json: dict, api: PleasantAPI):
        self.api = api
        self._entry_id = attachment_as_json["CredentialObjectId"]
        self._attachment_id = attachment_as_json["AttachmentId"]
        self.name = attachment_as_json["FileName"]

    @property
    def data(self) -> bytes:
        return self.api.get_attachment(self._entry_id, self._attachment_id)

    def __str__(self):
        return base64.b64encode(self.data).decode()

    def download(self, output_file_path: pathlib.Path = None):
        output_file_path = output_file_path or pathlib.Path(f"./{self.name}")
        output_file_path.write_bytes(self.data)


class Attachments(UserDict):
    def download(self, output_dir: pathlib.Path = None):
        output_dir = output_dir or pathlib.Path(f"./pleasant_attachments")
        if not output_dir.exists():
            output_dir.mkdir()

        for file_name, attachment in self.data.items():
            attachment.download(output_dir / file_name)


class Entry:
    def __init__(self, entry_as_json, api: PleasantAPI):
        self.api = api
        self._entry_id = entry_as_json["Id"]
        self.name = entry_as_json["Name"]
        self.username = entry_as_json["Username"]
        self.url = entry_as_json["Url"]
        self.custom_fields = entry_as_json["CustomUserFields"]

        attachments_as_dict = {}
        for attachment_as_json in entry_as_json["Attachments"]:
            attachments_as_dict[attachment_as_json["FileName"]] = Attachment(attachment_as_json, api)
        self.attachments = Attachments(attachments_as_dict)

    @property
    def password(self) -> str:
        return self.api.get_credential(self._entry_id)


class Folder(UserDict):
    def __init__(self, folder_as_json: dict, api: PleasantAPI):
        self.name = folder_as_json["Name"]
        entries = {entry_as_json["Name"]: Entry(entry_as_json, api) for entry_as_json in
                   folder_as_json["Credentials"]}
        folders = {folders_as_json["Name"]: Folder(folders_as_json, api) for folders_as_json in
                   folder_as_json["Children"]}
        super().__init__({**entries, **folders})


class Database(Folder):
    def __init__(self, api: PleasantAPI):
        super().__init__(api.get_db(), api)
