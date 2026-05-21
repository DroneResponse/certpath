# certpair

`certpair` is a small Python library for locating a matching client certificate and
private key on disk.

It looks for `.crt` and `.key` files that share the same stem and returns them as
`(cert_path, key_path)`, which makes the result easy to pass directly to clients
such as `requests`.

For example, suppose the `~/tls/` directory contains:
```
~/tls
❯ ls -1
user123.crt
user123.key

```

In this cae, both files share the same filename stem (that is `user123`). This python library would recognize these files as forming a "matching certificate and private key" because the stems match. 

Use this library when you want to:

- provide an easy way for Python applications to locate a certificate/private key pair using well-known environment variables, config files, and filesystem conventions
- search the current working directory for the best matching certificate pair
- search a specific directory for matching `.crt` and `.key` files
- start with either a certificate path or a key path and resolve the pair

Rather than writing custom logic to search the filesystem for a certificate-pair in every application, this library provides a reusable and convention-driven approach to certificate discovery. Applications automatically gain support for shared environment variables, config-file formats, and filesystem conventions.

Examples:

Given a config.json such as:

```json
{
  "sade_api_url": "https://api.sadezone.org",
  "public_cert": "/some/path/user123.crt",
  "private_key": "/another/path/user123.key",
  "tls_path": "~/tls"
}
```

Here's what you can do with this library:
```python
import certpair
import json

with open("config.json") as f:
    config = json.load(f)

# find the cert + key for the app by checking env vars or config file
cert, key = certpair.resolve(config)
# cert = "/some/path/user123.crt"
# key = "/another/path/user123.key"

# find a .crt and .key with the same stem in the current directory
cert, key = certpair.find()

# find a matching .crt and .key file in a directory
cert, key = certpair.find("~/tls")
# If more than one cert/key pair exists in this directory, then return the pair
# with the most recently modified certificate.

# Given either file in a certificate/key pair, locate the matching pair.
# Starting from the certificate path:
cert, key = certpair.find("~/tls/user123.crt") 
# Starting from the private key path:
cert, key = certpair.find("~/tls/user123.key")
# If a matching pair exists, both examples return:
# cert = "~/tls/user123.crt"
# key  = "~/tls/user123.key"
#
# Otherwise, find() returns None.
```

Here's a more complete example:
```python
import certpair
import requests

# find a .crt and .key with the same stem in the current directory
cert_pair = certpair.find()
# returns something like: ('/path/to/user123.crt', '/path/to/user123.key')

# use the cert_pair with the requests library:
resp = requests.get(
    f"https://api.example.com/",
    headers=_HEADERS,
    params=params,
    timeout=_TIMEOUT,
    cert=cert_pair,
)

# or use it with a requests.Session object:
session = requests.Session()
session.cert = certpair.find("~/tls/")
resp2 = session.get("https://api.example.com/")
```

## Config Details

When your application needs a certificate/key pair, you can use:
```python
certpair.resolve(config)
```
Pass a configuration dictionary that your application has already loaded from
JSON, TOML, YAML, or another source.

`resolve()` checks the following environment variables:

- `PUBLIC_CERT`: path to a `.crt` file
- `PRIVATE_KEY`: path to a `.key` file
- `TLS_PATH`: path to a directory containing matching `.crt` and `.key` files. If more than one pair exists then the one with the recently modified cert is selected.

When you pass a config dictionary to `resolve()`, it looks for these keys:

- `public_cert`: path to a `.crt` file
- `private_key`: path to a `.key` file
- `tls_path`: path to a directory containing matching `.crt` and `.key` files. If more than one pair exists then the one with the recently modified cert is selected.

Resolution order:

1. Environment variables `PUBLIC_CERT` and `PRIVATE_KEY`
2. Environment variable `TLS_PATH`
3. Config dictionary values `public_cert` and `private_key`
4. Config dictionary value `tls_path`
5. As a final fallback, the current working directory is searched for a matching `.crt` and `.key` pair

Environment variables take precedence over values from the config dictionary.
This means environment-provided values can be combined with config-based values
when only part of the configuration is supplied.

For example, if `PUBLIC_CERT` is set in the environment but `PRIVATE_KEY` is
not, then `resolve()` will attempt to combine the `PUBLIC_CERT` env var with the `private_key` value from the
config dictionary.

The working-directory is checked as the final fallback.

Example:

```python
import certpair
import json

with open("config.json") as f:
  config = json.load(f)

cert = certpair.resolve(config)
```

## Installation

For the fastest start, install directly from GitHub:

```bash
pip install git+https://github.com/DroneResponse/certpair@v1.1.1
```

If you want to pin that in `requirements.txt`:

```text
certpair @ git+https://github.com/DroneResponse/certpair@v1.1.1
```

### Install from Internal Package Index
If you have access to our internal package index (via Zero Tier), then you can install from there directly.

> [!IMPORTANT]
> Make sure `pip` is already configured to use the internal index before using the following two examples.
>
> To configure `pip` you can set this environment variable:
> ```
> export PIP_INDEX_URL="https://..."
> ```

To install using pip:
```bash
pip install certpair
```

To install using a `requirements.txt` file:

```text
certpair
```

## Development Setup

Create and activate a virtual environment, then install the project in editable mode with development dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

Or if you use `direnv` you can run:
```bash
direnv allow .
pip install -e ".[dev]"
```

## Running Tests

```bash
# from the project root
pytest
```

## Package and Release/Publish

```bash
bump-my-version bump '<patch | minor | major>'

devpi use '<package index URL>'
devpi login

devpi upload
```