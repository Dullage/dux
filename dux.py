import json
import random
from datetime import datetime

import click

from file import File

cli_help_text = """
A tool to augment the output of the duplicacy list command.

The output of the duplicacy list command can either be piped directly into dux
or into a file which can then be loaded by dux.

Note: The "-log" and "-files" options must be used in the duplicacy command.

Examples:

$ duplicacy -log list -r 45 -files | dux export-json -

\b
$ duplicacy -log list -r 45 -files > my_files.txt
$ dux export-json my_files.txt
"""


def find_existing_path(dict_: dict, path: list) -> tuple:
    """Return a tuple consisting of:
    - A pointer to any part of the path that already exists in the declared
    dict.
    - The remaining part of the path that needs to be created.
    """
    try:
        subfolder = path.pop(0)
    except IndexError:
        return (dict_, path)

    try:
        dict_ = dict_[subfolder]
        return find_existing_path(dict_, path)
    except KeyError:
        return (dict_, [subfolder] + path)


def create_missing_path(dict_: dict, path: list) -> dict:
    """Recursively create the specified path in the declared dict."""
    try:
        subfolder = path.pop(0)
        dict_[subfolder] = {}
        return create_missing_path(dict_[subfolder], path)
    except IndexError:
        return dict_


def add_file(base_folder, file_path, file_name, file_size):
    existing_path, missing_path = find_existing_path(base_folder, file_path)
    file_path = create_missing_path(existing_path, missing_path)
    file_path[file_name] = file_size


def default_output_filename():
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    return f"dux_{timestamp}.json"


def extract_files(input):
    files = []
    with click.progressbar(
        input.readlines(), label="Extracting Files"
    ) as input_:
        for line in input_:
            line_parts = line.strip().split(maxsplit=8)
            # 0 = Log Date
            # 1 = Log Time
            # 2 = Log Level
            # 3 = Log Type
            # 4 = File Size
            # 5 = Modified Date
            # 6 = Modified Time
            # 7 = File Hash (Blank if 0 File Size)
            # 8 = Path inc File Name (Index 7 if File Hash is blank)

            try:
                log_type = line_parts[3]
                if log_type == "SNAPSHOT_FILE":
                    size = int(line_parts[4])
                    path_idx = 8 if size > 0 else 7
                    path = line_parts[path_idx]
                    files.append(File(path, size))
            except IndexError:
                pass  # Line not in the correct format
    return files


@click.group(help=cli_help_text)
def cli():
    pass


# export-json command
@click.command(help="Export the file list to JSON.")
@click.argument("input", type=click.File(), required=True)
@click.option(
    "-o",
    "--output",
    type=click.File(mode="w"),
    default=default_output_filename(),
    help="Output file. Defaults to 'dux_<timestamp>.json'",
)
@click.option(
    "--indent",
    type=int,
    default=None,
    help="Number of spaces used to format JSON output. Defaults to None (unformatted).",  # noqa
)
def export_json(input, output, indent):
    file_list = extract_files(input)
    files = {}
    with click.progressbar(
        file_list, label="Exporting to JSON"
    ) as input_files_:
        for file in input_files_:
            add_file(files, file.directory_list, file.name, file.size)
    output.write(json.dumps(files, indent=indent))


# select-random command
@click.command(help="Select random files (useful for backup testing).")
@click.argument("input", type=click.File(), required=True)
@click.option(
    "--num-files",
    type=int,
    default=1,
    help="Number of random files to find.",
    show_default=True,
)
@click.option(
    "--min-size", type=int, help="Minimum size of random file in bytes."
)
@click.option(
    "--max-size", type=int, help="Maximum size of random file in bytes."
)
@click.option(
    "-x",
    "--exclude-extension",
    type=str,
    multiple=True,
    help="Exclude files from the random choice based on their extension. Multiple values allowed e.g. -x .txt -x .bak",  # noqa
)
def select_random(
    input,
    num_files,
    min_size,
    max_size,
    exclude_extension,
):
    file_list = extract_files(input)
    random.shuffle(file_list)
    chosen = []
    while len(chosen) < num_files and len(file_list) > 0:
        candidate = file_list.pop()
        if (
            candidate.extension not in exclude_extension
            and (min_size is None or candidate.size >= min_size)
            and (max_size is None or candidate.size <= max_size)
        ):
            chosen.append(candidate)

    for file in chosen:
        click.echo(f"- File: {file.path}")
        click.echo(f"  Size: {file.size} B")
    if len(chosen) != num_files:
        click.echo("Unable to find enough matching files!")


cli.add_command(export_json)
cli.add_command(select_random)


if __name__ == "__main__":
    cli()
