# pypleasant

pypleasant is a Python script and library to access
the [API](https://pleasantsolutions.com/info/pleasant-password-server/m-programmatic-access/restful-api) of
the [Pleasant Password Server](https://www.passwordserver.de).

```bash
pleasant-cli /path/to/entry --password # print password of credential entry
pleasant-cli /path/to/entry --attachments secret_file.txt # download attachments
pleasant-cli /path/to/entry --custom-field test # print values of custom fields
```

## Requirements

pypleasant requires Python >= 3.6 and only works with the Pleasant Password
Server [API v5](https://pleasantsolutions.com/info/pleasant-password-server/m-programmatic-access/restful-api-v5).

## Installation

The package is available on [PyPi](https://pypi.org/project/pypleasant/) and can easily be installed via pip:

```bash
pip install pypleasant
```

To use the command line client `pleasant-cli` you have to add your Python bin directory to your `PATH` variable.

```bash
export PATH+=$PATH:$HOME/.local/bin
```

Then you can call it:

```bash
pleasant-cli --help
```

Alternatively you can directly call it as a Python module without modifying your `PATH` variable:

```bash
python -m pypleasant --help
```

## Configuration

If you do not provide `pleasant-cli` with the login information to your Pleasant API you will be prompted for it. You
can also configure it completely or partially via command line parameter or environment variables:

+ `--api-url` or `PLEASANT_API_URL`
+ `--api-user` or `PLEASANT_API_USER`
+ `--api-password` (**NOT RECOMMENDED**) or `PLEASANT_API_PASSWORD`

Eventually you have to disable the HTTPS certificate check via `--disable-cert-check`
or `PLEASANT_DISABLE_CERT_CHECK=true` in case your server uses a self signed certificate.

## Usage

Printing attributes of an entry:

```bash
pleasant-cli /path/to/entry --username
pleasant-cli /path/to/entry --password
pleasant-cli /path/to/entry --url
```

Accessing the value of a custom field:

```bash
pleasant-cli /path/to/entry --custom-field test
```

Downloading attachments (default download directory is the current directory):

```bash
pleasant-cli /path/to/entry --attachments # downloads all attachments
pleasant-cli /path/to/entry --attachments secret_file.txt
pleasant-cli /path/to/entry --attachments file_1.txt file_2.txt --download-dir /path/to/download/dir
```

For a complete overview of all parameters call `pleasant-cli` with the help parameter:

```bash
> pleasant-cli --help
                       (--username | --password | --url | --custom-field [CUSTOM_FIELD] | --attachments [ATTACHMENTS [ATTACHMENTS ...]])
                       [--download-dir DOWNLOAD_DIR] [--api-url API_URL]
                       [--api-user API_USER] [--api-password API_PASSWORD]
                       [--disable-cert-check] [--verbose] [--debug]
                       path

positional arguments:
  path                  the path on the pleasant server to the credential
                        entry e.g. /Development/git (env var:
                        PLEASANT_PATH_TO_ENTRY)

optional arguments:
  -h, --help            show this help message and exit
  --username            print the username
  --password            print the password
  --url                 print the URL
  --custom-field [CUSTOM_FIELD]
                        print the given custom field
  --attachments [ATTACHMENTS [ATTACHMENTS ...]]
                        download the given attachment(s). if no attachment is
                        given all attachments are downloaded
  --download-dir DOWNLOAD_DIR
                        attachments are downloaded to this directory (DEFAULT:
                        '.', env var: PLEASANT_DOWNLOAD_DIR)
  --api-url API_URL     url of the pleasant server api (env var:
                        PLEASANT_API_URL)
  --api-user API_USER   user for the pleasant server api (env var:
                        PLEASANT_API_USER)
  --api-password API_PASSWORD
                        password for the pleasant server api (env var:
                        PLEASANT_API_PASSWORD)
  --disable-cert-check  disable HTTPS cert check (env var:
                        PLEASANT_DISABLE_CERT_CHECK)
  --verbose             activate verbose output
  --debug               activate debug output (env var: PLEASANT_DEBUG)
```
