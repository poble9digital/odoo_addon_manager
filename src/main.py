#!/usr/bin/env python3
import click
from git import Repo
from toml import load
from pathlib import Path
import shutil
@click.group()
@click.option('--config', type=click.Path(exists=False, file_okay=True, dir_okay=False), default="addons.toml")
@click.option('--destination', type=click.Path(exists=True, file_okay=False, dir_okay=True),default="addons")
@click.option('--cache', type=click.Path(), default=".repos")
@click.pass_context
def cli(ctx, cache, destination, config):
    """Odoo Addon Manager"""
    ctx.ensure_object(dict)
    ctx.obj['cache_path'] = Path(click.format_filename(cache))
    ctx.obj['dest_path'] = Path(click.format_filename(destination))
    ctx.obj['config_path'] = Path(click.format_filename(config))
    try:
        with open(click.format_filename(config)) as config_file:
            config_dict = load(config_file)
            if config_dict.get('repos',  []) == []:
                raise click.BadParameter("Config file doesn't contain any repos")
            ctx.obj['CONFIG'] = config_dict
    except FileNotFoundError:
        click.echo(f"Error: Config file {ctx.obj['config_path']} not found.", err=True)
    except click.BadParameter:
        click.echo(f"Error: Config file {ctx.obj['config_path']} doesn't contain any repos", err=True)

@cli.command()
@click.pass_context
def clone_repos(ctx):
    repos = ctx.obj['CONFIG']['repos']
    if not ctx.obj['cache_path'].exists():
        ctx.obj['cache_path'].mkdir()
    with click.progressbar(repos, label="Cloning Repos") as progress_repos:
        for repo in progress_repos:
            repo_name = repo['url'].split("/")[-1]
            repo_path = ctx.obj['cache_path'] / repo_name
            click.echo(f"Updating {repo['url'].split("/")[-1]}")
            if not repo_path.exists():
                Repo.clone_from(repo['url'], str(repo_path),branch=repo['branch'], depth=1)
            else:
                Repo(str(repo_path)).remotes.origin.pull()

@cli.command()
@click.option('--update-repos/--no-update-repos', default=True, help='Update repos')
@click.pass_context
def list_addons(ctx, update_repos):
    if update_repos:
        ctx.invoke(clone_repos)
    click.echo("Available addons:")
    for repo in ctx.obj['cache_path'].iterdir():
        for folder in repo.iterdir():
            if folder.is_dir() and (folder / "__manifest__.py").exists():
                click.echo(f" - {folder.name}")
@cli.command()
@click.option('--update-repos/--no-update-repos', default=True, help='Update repos')
@click.pass_context      
def copy_addons(ctx, update_repos):
    if update_repos:
        ctx.invoke(clone_repos)
    for repo in ctx.obj['cache_path'].iterdir():
        for folder in repo.iterdir():
            if folder.is_dir() and (folder / "__manifest__.py").exists() and folder.name in ctx.obj['CONFIG']['addons']:
                click.echo(f"Installing {folder.name}")
                destination = ctx.obj['dest_path'] / folder.name
                shutil.copytree(folder, destination, dirs_exist_ok=True)

if __name__ == '__main__':
    cli()
