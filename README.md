# dux

A tool to augment the output of the `duplicacy list -files` command.

## Usage

```
Usage: dux [OPTIONS] COMMAND [ARGS]...

  A tool to augment the output of the duplicacy list command.

  The output of the duplicacy list command can either be piped directly into
  dux or into a file which can then be loaded by dux.

  Note: The "-log" and "-files" options must be used in the duplicacy
  command.

  Examples:

  $ duplicacy -log list -r 45 -files | dux -

  $ duplicacy -log list -r 45 -files > my_files.txt
  $ dux my_files.txt

Options:
  --help  Show this message and exit.

Commands:
  export-json    Export the file list to JSON.
  select-random  Select random files (useful for backup testing).
```

## export-json
Turns the output of the `duplicacy list -files` command:

```log
...
2020-10-24 11:39:31.338 INFO SNAPSHOT_FILE  783 2020-10-24 11:38:27 fd714a3cddef70c7c99383385021ab3d2316fd1864b2887ccf0bfdaf2c797afd Notes.txt
2020-10-24 11:39:31.338 INFO SNAPSHOT_FILE 981570 2020-08-15 14:29:08 654609f5385591ea239a1ee4ecaeccfde806fcafbe4b9dacfc548955a49f34c0 Photos/beach.jpg
2020-10-24 11:39:31.338 INFO SNAPSHOT_FILE 3359200 2020-10-04 10:45:18 b396c2a94e14777dbf1b744e6ad0164f3d2d998ea15d24085588cba9fed1abab Photos/house.jpg
...
```

Into JSON: 
```json
{
  "Notes.txt": 783,
  "Photos": {
    "beach.jpg": 981570,
    "house.jpg": 3359200
  }
}
```

```
Usage: dux.py export-json [OPTIONS] INPUT

  Export the file list to JSON.

Options:
  -o, --output FILENAME  Output file. Defaults to 'dux_<timestamp>.json'
  --indent INTEGER       Number of spaces used to format JSON output. Defaults
                         to None (unformatted).

  --help                 Show this message and exit.
```

The output can then easily be explored using tools such as [fx](https://github.com/antonmedv/fx) or even in Firefox which has a decent inbuilt JSON browser.

# select-random

Select random files (useful for backup testing).

```
Usage: dux.py select-random [OPTIONS] INPUT

  Select random files (useful for backup testing).

Options:
  --num-files INTEGER           Number of random files to find.  [default: 1]
  --min-size INTEGER            Minimum size of random file in bytes.
  --max-size INTEGER            Maximum size of random file in bytes.
  -x, --exclude-extension TEXT  Exclude files from the random choice based on
                                their extension. Multiple values allowed e.g.
                                -x .txt -x .bak

  --help                        Show this message and exit.
```
