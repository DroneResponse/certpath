import pytest
from pathlib import Path

from certpair import SelectionStrategy, find, resolve


def test_find_selects_alice_for_alphabetical_strategy() -> None:
    result = find("tests/tls", SelectionStrategy.ALPHABETICAL)

    assert result is not None
    cert_path, key_path = result
    assert Path(cert_path).name == "alice.crt"
    assert Path(key_path).name == "alice.key"


def test_expand_home_dir() -> None:
    if not Path.cwd().is_relative_to(Path.home()):
        pytest.skip("Current working directory is not relative to home directory, so cannot test ~ expansion.")
        return

    rel_path = str(Path.cwd().relative_to(Path.home()))
    tls_dir = Path(f"~/{rel_path}/tests/tls")

    result = find(tls_dir, SelectionStrategy.ALPHABETICAL)

    assert result is not None
    cert_path, key_path = result
    assert Path(cert_path).name == "alice.crt"
    assert Path(key_path).name == "alice.key"


def test_resolve_uses_config_dict_when_env_is_unset(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PUBLIC_CERT", raising=False)
    monkeypatch.delenv("PRIVATE_KEY", raising=False)
    monkeypatch.delenv("TLS_PATH", raising=False)

    cert_file = tmp_path / "client.crt"
    key_file = tmp_path / "client.key"
    cert_file.write_text("cert")
    key_file.write_text("key")

    result = resolve({
        "public_cert": str(cert_file),
        "private_key": str(key_file),
    })

    assert result == (str(cert_file), str(key_file))


def test_resolve_prefers_env_over_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_cert = tmp_path / "config.crt"
    config_key = tmp_path / "config.key"
    env_cert = tmp_path / "env.crt"
    env_key = tmp_path / "env.key"

    config_cert.write_text("config cert")
    config_key.write_text("config key")
    env_cert.write_text("env cert")
    env_key.write_text("env key")

    monkeypatch.setenv("PUBLIC_CERT", str(env_cert))
    monkeypatch.setenv("PRIVATE_KEY", str(env_key))
    monkeypatch.delenv("TLS_PATH", raising=False)

    result = resolve({
        "public_cert": str(config_cert),
        "private_key": str(config_key),
    })

    assert result == (str(env_cert), str(env_key))
