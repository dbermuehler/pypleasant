import argparse
import logging
import os
import pathlib
import sys
from getpass import getpass
from typing import Tuple, List

import requests

from pypleasant.api import PleasantAPI, BadCredentials
from pypleasant.artifacts import Database, Entry
from pypleasant.pathparser import PathParser, PleasantElementNotFound


def parse_cmd() -> Tuple[str, str, str, List[str], pathlib.Path, str, str, str, bool]:
    parser = argparse.ArgumentParser("pleasant-client")
    attribute_group = parser.add_mutually_exclusive_group(required=True)
    attribute_group.add_argument("--username", action="store_true", help="print the username")
    attribute_group.add_argument("--password", action="store_true", help="print the password")
    attribute_group.add_argument("--url", action="store_true", help="print the URL")
    attribute_group.add_argument("--custom-field", type=str, nargs='?',
                                 help="print the given custom field")
    attribute_group.add_argument("--attachments", type=str, nargs='*',
                                 help="download the given attachment(s); if no attachment is given, all attachments are downloaded")

    parser.add_argument("--download-dir", type=str,
                        help="attachments are downloaded to this directory (DEFAULT: '.', env var: PYPLEASANT_DOWNLOAD_DIR)")

    parser.add_argument("--api-url", type=str, help="URL of the pleasant server API (env var: PYPLEASANT_API_URL)")
    parser.add_argument("--api-user", type=str, help="user for the pleasant server API (env var: PYPLEASANT_API_USER)")
    parser.add_argument("--api-password", type=str,
                        help="password for the pleasant server API (env var: PYPLEASANT_API_PASSWORD)")
    parser.add_argument("--disable-cert-check", action="store_true",
                        help="disable HTTPS cert check (env var: PYPLEASANT_DISABLE_CERT_CHECK)",
                        dest="disable_cert_check")
    parser.add_argument("--verbose", action="store_true", help="activate verbose output")
    parser.add_argument("--debug", action="store_true", help="activate debug output (env var: PYPLEASANT_DEBUG)")

    parser.add_argument("path", type=str,
                        help="the path on the pleasant server to the credential entry, e.g. /Development/git (env var: PYPLEASANT_PATH_TO_ENTRY)")
    args = parser.parse_args()

    if args.username:
        entry_attribute = "username"
    elif args.password:
        entry_attribute = "password"
    elif args.url:
        entry_attribute = "url"
    elif args.custom_field:
        entry_attribute = "custom_field"
    else:
        entry_attribute = "attachments"

    custom_field_key = args.custom_field
    attachment_file_names = args.attachments
    download_dir = args.download_dir or os.getenv("PYPLEASANT_DOWNLOAD_DIR") or '.'

    api_url = args.api_url or os.getenv("PYPLEASANT_API_URL") or input("Pleasant Server URL: ")
    api_user = args.api_user or os.getenv("PYPLEASANT_API_USER") or input("Pleasant User: ")
    api_password = args.api_password or os.getenv("PYPLEASANT_API_PASSWORD") or getpass()
    disable_cert_check = args.disable_cert_check or os.getenv("PYPLEASANT_DISABLE_CERT_CHECK", "").lower() == "true"
    verify_https = not disable_cert_check

    activate_debug = args.debug or os.getenv("PYPLEASANT_DEBUG")
    if activate_debug:
        logging.root.setLevel(logging.DEBUG)
    elif args.verbose:
        logging.root.setLevel(logging.INFO)

    path = args.path or os.getenv("PYPLEASANT_PATH_TO_ENTRY")

    return path, entry_attribute, custom_field_key, attachment_file_names, pathlib.Path(
        download_dir), api_url, api_user, api_password, verify_https


def print_prettified_exception(exception: BaseException) -> None:
    prettify_output = logging.root.level == logging.DEBUG
    if not prettify_output:
        raise exception
    else:
        standard_error_message = "Internal error. For more details activate debug output with --debug"
        logging.error(exception.args[0] if exception.args else standard_error_message)


class NotAPleasantEntry(Exception):
    def __init__(self, path: str):
        super().__init__(f"{path} is not an entry")


class PleasantAPIConnectionError(Exception):
    def __init__(self, url: str):
        super().__init__(f"Could not connect to {url}")


def lookup(url: str, user: str, password: str, verify_https: bool, path: str) -> Entry:
    api = PleasantAPI(url, user, password, verify_https)
    database = Database(api)
    entry = PathParser(database).lookup(path)

    if not isinstance(entry, Entry):
        raise NotAPleasantEntry(path)
    else:
        return entry


def main() -> None:
    logging.basicConfig(stream=sys.stderr,
                        level=logging.DEBUG if os.getenv("PYPLEASANT_DEBUG") else None,
                        format="%(levelname)s: %(message)s")

    try:
        path, entry_attribute, custom_field_key, attachment_file_names, download_dir, api_url, api_user, api_password, verify_https = parse_cmd()

        entry = lookup(api_url, api_user, api_password, verify_https, path)
        if entry_attribute == "username":
            print(entry.username)
        elif entry_attribute == "password":
            print(entry.password)
        elif entry_attribute == "url":
            print(entry.url)
        elif entry_attribute == "custom_field":
            print(entry.custom_fields[custom_field_key])
        elif entry_attribute == "attachments":
            attachment_file_names = attachment_file_names if attachment_file_names else [file_name for file_name in
                                                                                         entry.attachments]
            for file_name in attachment_file_names:
                print(f"{path}: {file_name} -> {download_dir / file_name}")
                entry.attachments[file_name].download(download_dir / file_name)
    except BadCredentials as e:
        print_prettified_exception(e)
    except NotAPleasantEntry as e:
        print_prettified_exception(e)
    except PleasantElementNotFound as e:
        print_prettified_exception(e)
    except requests.exceptions.ConnectionError as e:
        print_prettified_exception(PleasantAPIConnectionError(e.request.url))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print_prettified_exception(e)
