# certpair

`certpair` is a small Python library for locating a matching client certificate and
private key on disk.

It looks for `.crt` and `.key` files that share the same stem and returns them as
`(cert_path, key_path)`, which makes the result easy to pass directly to clients
such as `requests`.

Use it when you want to:

- search the current working directory for the best matching certificate pair
- search a specific directory for matching `.crt` and `.key` files
- start from either the certificate path or key path and resolve the pair

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

# find a matching .crt and .key file in the same directory given a file path to one of them
cert, key = certpair.find("~/tls/user123.crt")
cert, key = certpair.find("~/tls/user123.key")
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

session = requests.Session()
session.cert = certpair.find("~/tls/")
```

## Installation

For the fastest start, install directly from GitHub:

```bash
pip install git+https://github.com/DroneResponse/certpair@v1.0.0
```

If you want to pin that in `requirements.txt`:

```text
certpair @ git+https://github.com/DroneResponse/certpair@v1.0.0
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