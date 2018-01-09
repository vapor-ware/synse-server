#!/usr/bin/env python
"""
synseport is a tool for porting commits from synse-server to
synse-server-internal and vice versa.
"""

import argparse
import logging
import os
import sys
from subprocess import PIPE, Popen, CalledProcessError
import yaml

from commit_data import CommitData  # pylint: disable=relative-import
from data_file import DataFile  # pylint: disable=relative-import
from data_file_line import DataFileLine  # pylint: disable=relative-import

# Setup logging.
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Set to DEBUG for detailed traces.


# Global constants.
INTERNAL_REPO_ARGS = ['i', 'internal', 'synse-server-internal']
SYNSE_REPO_ARGS = ['s', 'synse', 'synse-server']


def _add_data_lines(commit_data, data_file):
    """
    Add lines to the data file for the commits in commit_data.
    :param commit_data: CommitData not in the data file.
    :param data_file: The DataFile to add the commit_data to.
    """
    for cd in commit_data:
        line = DataFileLine(cd.hash, cd.author, cd.message)
        data_file.append(line)
    data_file.write()


def _execute(cmd):
    """
    Execute an arbitrary command line.
    :param cmd: The command line to execute.
    :return: stdout, stderr.
    :raises: Return code of the command line is not zero.
    """
    proc = Popen(args=cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, error = proc.communicate()
    if proc.returncode != 0:
        raise CalledProcessError(proc.returncode, cmd, out)
    return out, error


def _execute_git(directory, cmd):
    """
    Execute a git command. There is no constraint that cmd is a git command,
    but that's what we're using it for.
    :param directory: The directory on the local machine to run the command in.
    :param cmd: The git command to run.
    :return: stdout, stderr
    """
    cur_dir = os.getcwd()
    try:
        os.chdir(directory)
        out, err = _execute(cmd)
        return out, err
    finally:
        os.chdir(cur_dir)


def _find_hash(data_file, _hash):
    """
    Find the given git commit hash in the data_file.
    :param data_file: The loaded data file to find the hash in.
    :param _hash: The git commit hash to find.
    :return: The DataFileLine if found, else None.
    """
    for line in data_file.lines:
        if line.hash == _hash:
            return line
    return None


def _find_untracked_commits(git_log, data_file):
    """
    Find commits in the git log that are not tracked in the data file.
    :param git_log: The git log as a list of CommitData.
    :param data_file: The data file for the repo.
    :return: A list of CommitData in the git log that are not in the data file.
    """
    # This algorithm is not efficient. (Hashtable is better.)
    logger.debug('Finding hashes:')
    not_found = []  # List of hashes in the git log, but not the data file.
    for commit_data in git_log:
        found = False
        for data_line in data_file.lines:
            logger.debug('commit_data.hash: {}, data_line.hash: {}'.format(
                commit_data.hash, data_line.hash))
            if commit_data.hash == data_line.hash:
                found = True
                break

        if found:
            logger.debug('Found hash: {}'.format(commit_data.hash))
        else:
            logger.debug('Hash not found: {}'.format(commit_data.hash))
            not_found.append(commit_data)

    logger.debug('not_found: {}'.format(not_found))
    return not_found


def _get_config(config_file_name='.synseport.yml'):
    """Reads the synse-server and synse-server-internal directories from the
    .synseport.yml file in the local directory.
    :param config_file_name: The name of the synseport yaml configuration file.
    :returns: The yaml configuration.
    :raises: ValueError when keys are not present or values are not set
    correctly."""
    with open(config_file_name, 'r') as stream:
        config = yaml.load(stream)

        # Be sure that the config contains what we need and the directories exist.
        # Check keys.
        if 'SYNSE_SERVER_GIT_DIRECTORY' not in config:
            raise ValueError(
                'Config file {} contains no key '
                'SYNSE_SERVER_GIT_DIRECTORY'.format(config_file_name))
        if 'SYNSE_SERVER_INTERNAL_GIT_DIRECTORY' not in config:
            raise ValueError(
                'Config file {} contains no key '
                'SYNSE_SERVER_INTERNAL_GIT_DIRECTORY'.format(config_file_name))

        # Check values are directories that exist.
        synse_dir = config['SYNSE_SERVER_GIT_DIRECTORY']
        internal_dir = config['SYNSE_SERVER_INTERNAL_GIT_DIRECTORY']

        if not os.path.isdir(synse_dir):
            raise ValueError(
                'Directory {} in config file {} does not exist.'.format(
                    synse_dir, config_file_name))
        if not os.path.isdir(internal_dir):
            raise ValueError(
                'Directory {} in config file {} does not exist.'.format(
                    internal_dir, config_file_name))
        logger.debug('config: {}'.format(config))

        # Check that GIT_USER is set.
        if 'GIT_USER' not in config:
            raise ValueError('Config file {} contains no key GIT_USER'.format(
                config_file_name))
        return config


def _get_other_repo_data_file(repo):
    """
    Get the data file for the other repo and read it.
    :param repo: The repo argument from the command line.
    line.
    :return: The data file for the other repo.
    """
    # These data_file_names are flopped.
    if repo in SYNSE_REPO_ARGS:
        data_file_name = 'synse-server-internal.csv'
    elif repo in INTERNAL_REPO_ARGS:
        data_file_name = 'synse-server.csv'
    else:
        raise ValueError(
            'Invalid repo argument. Expected '
            '{s|synse|synse-server|i|internal|synse-server-internal}')

    # Load and return the data file.
    return _load_data_file(data_file_name)


def _get_repo_data_file(repo):
    """
    Get the data file and read it given the repo argument.
    :param repo: The repo argument from the command line.
    :return: The data file for the given repo.
    """
    if repo in SYNSE_REPO_ARGS:
        data_file_name = 'synse-server.csv'
    elif repo in INTERNAL_REPO_ARGS:
        data_file_name = 'synse-server-internal.csv'
    else:
        raise ValueError(
            'Invalid repo argument. Expected '
            '{s|synse|synse-server|i|internal|synse-server-internal}')

    # Load and return the data file.
    return _load_data_file(data_file_name)


def _load_data_file(data_file_name):
    """
    Load the DataFile with name data_file_name.
    :param data_file_name: The name of the data file to load.
    :return: The DataFile.
    """
    data_file = DataFile(data_file_name)
    data_file.read()
    return data_file

def _mark(config, args):
    """
    Update the data files for both the synse-server-inrternal and synse-server
    git repos with any new commits.
    :param config: The yaml config.
    :param args: The command line arguments.
    """
    logger.debug('_mark({}, {}'.format(config, args))
    logger.debug('_mark() args.git_repo:      {}'.format(args.git_repo))
    logger.debug('_mark() args.commit:        {}'.format(args.commit))
    logger.debug('_mark() args.remote_commit: {}'.format(args.remote_commit))
    logger.debug('_mark() args.status:        {}'.format(args.status))
    logger.debug('_mark() args.notes:         {}'.format(args.notes))

    # Use / load the data file corresponding to the given repo.
    data_file_local = _get_repo_data_file(args.git_repo)

    # Find the line_local to update.
    line_local = _find_hash(data_file_local, args.commit)
    if line_local is None:
        raise ValueError('Unable to find commit hash {}.'.format(args.commit))

    # If args.status is not unnecessary, we will need to cross link the data
    # files, so ensure the remote commit exists prior to updating anything.
    # If the remote commit does not exist, this find will raise and nothing
    # shall be updated.
    if args.status != 'u' and args.status != 'unnecessary' \
            and args.status != 'o' and args.status != 'open':
        data_file_remote = _get_other_repo_data_file(args.git_repo)

        # Find the remote line to update.
        line_remote = _find_hash(data_file_remote, args.remote_commit)
        if line_remote is None:
            raise ValueError('Unable to find remote_commit hash {}.'.format(args.remote_commit))
    else:
        data_file_remote = None
        line_remote = None

    # Update local fields.
    line_local.update_status(args.status)
    line_local.update_porter(config['GIT_USER'])
    line_local.update_remote_commit(args.remote_commit)
    line_local.update_notes(args.notes)

    # Write the local data file.
    data_file_local.write()

    if line_remote is not None:
        # Update remote fields.
        line_remote.update_status(args.status)
        line_remote.update_porter(config['GIT_USER'])
        line_remote.update_remote_commit(args.commit)
        line_remote.update_notes(args.notes)

        # Write the remote data file.
        data_file_remote.write()


def _parse_args():
    """
    Parse command line arguments.
    :return: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-u', '--update',
        help='Update data files with git commits.',
        action='store_true')

    parser.add_argument(
        '-m', '--mark',
        help='Mark a commit as ported.',
        action='store_true')

    parser.add_argument(
        '-g', '--git-repo',
        type=str,
        help='Git repo to mark {s|synse|synse-server|i|internal|synse-server-internal}.')

    parser.add_argument(
        '-c', '--commit',
        type=str,
        help='Git commit hash to mark.')

    parser.add_argument(
        '-r', '--remote-commit',
        type=str,
        help='Git commit hash in the remote repo.')

    parser.add_argument(
        '-s', '--status',
        type=str,
        help='Status to mark {o|open|u|unnecessary|c|completed}.')

    parser.add_argument(
        '-n', '--notes',
        type=str,
        help='Arbitrary notes as single string.')

    args = parser.parse_args()
    logger.debug('args: {}'.format(args))
    logger.debug('dir(args): {}'.format(dir(args)))
    return args


def _read_git_log(directory):
    """
    Read the git log from a directory.
    :param directory: The directory to run the git log command from.
    :return: The a list of CommitData for each commit in the log.
    """
    cmd = ['git', '--no-pager', 'log', """--format='%h;;%an;;%s'""", '--since=2017-09-31']
    out, err = _execute_git(directory, cmd)
    logger.debug('git log {} out: {}'.format(directory, out))
    logger.debug('git log {} err: {}'.format(directory, err))

    # Split across newlines.
    commits = out.splitlines()
    logger.debug('commits: {}'.format(commits))

    # Create list of CommitData. Reverse the log results here.
    result = []
    for commit in reversed(commits):
        split = commit.split(';;', 2)
        _hash = split[0][1:]
        author = split[1]
        message = split[2][:-1][:60].replace(',', ' ')
        result.append(CommitData(_hash, author, message))
    return result


def _update(config):
    """
    Update the data files for both the synse-server-inrternal and synse-server
    git repos with any new commits.
    :param config: The yaml config.
    """
    _update_by_repo(config['SYNSE_SERVER_INTERNAL_GIT_DIRECTORY'], True)
    _update_by_repo(config['SYNSE_SERVER_GIT_DIRECTORY'], False)


def _update_by_repo(directory, is_internal):
    """
    Update the data files for a git repo with any new commits.
    :param directory: The directory of the git repo.
    :param is_internal: True for synse-server-internal, False for synse-server.
    """
    # Read the git log.
    git_log = _read_git_log(directory)

    # Read the data file.
    if is_internal:
        data_file = DataFile('synse-server-internal.csv')
    else:
        data_file = DataFile('synse-server.csv')
    data_file.read()

    # Debug traces.
    logger.debug('Data for git repo {}'.format(directory))
    logger.debug('internal_log:  {}, len: {}'.format(git_log, len(git_log)))
    logger.debug('internal_data: {}, len: {}'.format(data_file, len(data_file.lines)))

    # For each line in the git log:
    # Find rows where the hash is not in the data file.
    not_found = _find_untracked_commits(git_log, data_file)

    # Add rows not found and write out the data file.
    _add_data_lines(not_found, data_file)


def main():
    """
    Main entry point.
    :return: 0 on success.
    """
    logger.debug('main start')
    config = _get_config()
    args = _parse_args()
    logger.debug('args.update: {}'.format(args.update))

    if args.update:
        _update(config)
    if args.mark:
        _mark(config, args)
    logger.debug('main end')


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Exception as e:  # pylint: disable=bare-except
        logger.exception(e)
        sys.exit(1)
