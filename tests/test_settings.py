import pytest

from danfoss_ecl import dump
from danfoss_ecl.dump import SettingsError, load_env_files, load_settings, parse_args

ECL_VARS = (
    "ECL310_HOST",
    "ECL310_MODBUS_MODE",
    "ECL310_PORT",
    "ECL310_UNIT_ID",
    "ECL310_APP",
)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    # setenv first so monkeypatch records the variable and removes whatever
    # load_dotenv() writes into os.environ during the test.
    for name in ECL_VARS:
        monkeypatch.setenv(name, "")
        monkeypatch.delenv(name)


def test_loads_ecl310_a266_env_from_cwd(tmp_path, monkeypatch):
    (tmp_path / "ecl310_a266.env").write_text("ECL310_HOST=192.0.2.10\nECL310_UNIT_ID=5\n")
    monkeypatch.chdir(tmp_path)
    assert load_env_files() == [tmp_path / "ecl310_a266.env"]
    settings = load_settings()
    assert settings.host == "192.0.2.10"
    assert settings.unit_id == 5


def test_no_settings_file_returns_empty(tmp_path):
    assert load_env_files(cwd=tmp_path) == []


def test_ecl310_a266_env_wins_over_dot_env(tmp_path):
    (tmp_path / "ecl310_a266.env").write_text("ECL310_HOST=192.0.2.10\n")
    (tmp_path / ".env").write_text("ECL310_HOST=192.0.2.99\nECL310_PORT=1502\n")
    assert load_env_files(cwd=tmp_path) == [tmp_path / "ecl310_a266.env", tmp_path / ".env"]
    settings = load_settings()
    assert settings.host == "192.0.2.10"
    assert settings.port == 1502


def test_real_environment_wins_over_file(tmp_path, monkeypatch):
    (tmp_path / "ecl310_a266.env").write_text("ECL310_HOST=192.0.2.10\n")
    monkeypatch.setenv("ECL310_HOST", "192.0.2.20")
    load_env_files(cwd=tmp_path)
    assert load_settings().host == "192.0.2.20"


def test_host_argument_wins(tmp_path, monkeypatch):
    monkeypatch.setenv("ECL310_HOST", "192.0.2.20")
    assert load_settings(host="192.0.2.30").host == "192.0.2.30"


def test_explicit_env_file(tmp_path):
    path = tmp_path / "other.env"
    path.write_text("ECL310_HOST=192.0.2.40\n")
    (tmp_path / "ecl310_a266.env").write_text("ECL310_HOST=192.0.2.10\n")
    assert load_env_files(path, cwd=tmp_path) == [path]
    assert load_settings().host == "192.0.2.40"


def test_missing_explicit_env_file(tmp_path):
    with pytest.raises(SettingsError, match="not found"):
        load_env_files(tmp_path / "missing.env")


def test_tcp_without_host_is_an_error():
    with pytest.raises(SettingsError, match="ECL310_HOST"):
        load_settings()


def test_rtu_does_not_need_host(monkeypatch):
    monkeypatch.setenv("ECL310_MODBUS_MODE", "rtu")
    assert load_settings().mode == "rtu"


def test_invalid_mode(monkeypatch):
    monkeypatch.setenv("ECL310_MODBUS_MODE", "udp")
    with pytest.raises(SettingsError, match="tcp"):
        load_settings(host="192.0.2.1")


def test_main_exits_without_host(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc:
        dump.main([])
    assert "ECL310_HOST" in str(exc.value.code)


def test_parse_args():
    args = parse_args(["--host", "192.0.2.1", "--env-file", "x.env"])
    assert args.host == "192.0.2.1"
    assert str(args.env_file) == "x.env"
