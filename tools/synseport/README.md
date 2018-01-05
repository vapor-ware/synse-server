# synseport 
Synseport is a tool for porting commits from synse-server to
synse-server-internal and vice versa.

## Problem Statement
We have forked the synse-server repo into:

* synse-server: public open-source repo.
* synse-server-internal: private Vapor IO repo.

The main difference between the two is the daemons and tools that are only in
the synse-server-internal repo. The reason for the full repo fork is that git
does not support private branches pushed up to public repo.

What's happening is that some commits are going into one repo or the other but
not both. This tool provides a tracking mechanism for linking the commits in
each repo with a sign off column showing that each commit is open, unnecessary,
or completed.

## Configuration
Add a file to the local directory called .synseport.yml containing the
directories of the synse-server and synse-server-internal directories on the 
local machine.

```
# Locations of the synse-server and synse-server-internal repos on the local machine.
SYNSE_SERVER_GIT_DIRECTORY: /Users/mhink/src/vapor/synse-server
SYNSE_SERVER_INTERNAL_GIT_DIRECTORY: /Users/mhink/src/vapor/synse-server-internal

# Friendly name of the current user / git author.
# This may differ from the github login.
# This is the output of: git config user.name
# Examples:
# - MatthewHink
# - Erick Daniszewski
# - Tim
GIT_USER: MatthewHink
```

## Sample Usage

Show command line help (long and short forms):
```bash
./synseport.py -h
./synseport.py -help
```

Update the spreadsheets with all of the commits in the git log output for each
repo (long and short forms):
```bash
./synseport.py -u
./synseport.py -update
```

Show each spreadsheet (mac, should work on Windows):
```bash
open *.csv
```

Mark the spreadsheet for the synse-server-internal repo.
Set local commit 590d02c to b5f4df6 in synse-server.
Set status completed.
Set notes to Test Notes.

```bash
./synseport.py -m -g i -c 590d02c -r b5f4df6 -s c -n 'Test notes'
./synseport.py --mark --git-repo internal --commit 590d02c --remote-commit b5f4df6 --status completed --notes 'Test notes'
```

