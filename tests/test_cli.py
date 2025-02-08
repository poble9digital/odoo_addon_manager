from pathlib import Path
from click.testing import CliRunner
import pytest
from main import cli
from os import listdir

example_config = """
addons = [
    "openupgrade_framework",
]

[[repos]]
url = "https://github.com/OCA/OpenUpgrade"
branch = "17.0"
"""

@pytest.fixture
def example_dir(tmp_path):
    cache = tmp_path / "cache"  
    config = tmp_path / "config.toml"
    destination = tmp_path / "addons"
    config.write_text(example_config)
    cache.mkdir()
    destination.mkdir()
    return (tmp_path, cache, config, destination)

def test_list(example_dir):
    example_output = """Cloning Repos
Updating OpenUpgrade
Available addons:
 - openupgrade_framework
 - openupgrade_scripts
"""
    tmp_path, cache, config, destination = example_dir
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        result = runner.invoke(cli, ['--config', config, '--destination', destination, '--cache', cache, 'list-addons'])
        print(result.output)
        assert result.exit_code == 0
        assert result.output == example_output
def test_no_config(example_dir):
    tmp_path, cache, config, destination = example_dir
    example_output = """Error: Config file no_config.toml not found.\n"""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        result = runner.invoke(cli, ['--config', "no_config.toml", '--destination', destination, '--cache', cache, 'list-addons'])
        print(result.output)
        assert result.exit_code == 1
        assert result.output == example_output
def test_config_empty(example_dir):
    tmp_path, cache, config, destination = example_dir
    empty_config = tmp_path / "empty.toml"
    empty_config.write_text("")
    example_output = f"""Error: Config file {empty_config} doesn't contain any repos\n"""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        result = runner.invoke(cli, ['--config', empty_config, '--destination', destination, '--cache', cache, 'list-addons'])
        print(result.output)
        assert result.exit_code == 1
        assert result.output == example_output
def test_install(example_dir):
    tmp_path, cache, config, destination = example_dir
    example_output = """Cloning Repos
Updating OpenUpgrade
Installing openupgrade_framework\n"""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        result = runner.invoke(cli, ['--config', config, '--destination', destination, '--cache', cache, 'copy-addons'])
        print(result.output)
        assert result.exit_code == 0
        assert result.output == example_output