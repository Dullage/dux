import json
from datetime import datetime

import click

cli_help_text = """
Convert the output of the duplicacy list command to JSON.

The output of the duplicacy list command can either be piped directly into dux
or into a file which can then be loaded by dux. Note: The "-log" and "-files"
options must be used in the duplicacy command.

Examples:

duplicacy -log list -r 45 -files | dux -

duplicacy -log list -r 45 -files > my_files.txt && dux my_files.txt
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


def main(input, output, indent=None):
    files = {}

    with click.progressbar(input.readlines()) as input_:
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
                    file_size = int(line_parts[4])
                    file_path_idx = 8 if file_size > 0 else 7
                    file_path = line_parts[file_path_idx].split("/")
                    file_name = file_path.pop(-1)

                    add_file(files, file_path, file_name, file_size)
            except IndexError:
                pass  # Line not in the correct format

    output.write(json.dumps(files, indent=indent))


@click.command(help=cli_help_text)
@click.argument("input", type=click.File(), required=True)
@click.option(
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
def cli(input, output, indent):
    main(input, output, indent)


if __name__ == "__main__":
    cli()
