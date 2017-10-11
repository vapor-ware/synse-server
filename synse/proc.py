"""

"""

import os

from synse.proto.client import get_client


class ProcManager(object):
    """ Manager for registered background processes.
    """

    def __init__(self):
        self.processes = {}

    def get(self, name):
        """ Get the named BGProc instance by name.

        Args:
            name (str): the name of the BGProc to get.

        Returns:
            BGProc: the BGProc instance with the matching name.
            None: if the given name does not correspond to a managed
                BGProc instance.
        """
        return self.processes.get(name)

    def add(self, bgproc):
        """ Add a new BGProc to the managed dictionary.

        Args:
            bgproc (BGProc): the background process object to
                add to the managed dictionary.
        """
        if not isinstance(bgproc, BGProc):
            raise ValueError(
                'Only BGProc instances can be added to the manager.'
            )

        name = bgproc.name
        if name in self.processes:
            raise ValueError(
                'The given BGProc ("{}") already exists in the managed '
                'dictionary.'.format(name)
            )

        self.processes[name] = bgproc


class BGProc(object):
    """ Class which holds the relevant information for a background
    process for Synse.
    """
    manager = None

    def __init__(self, name, sock):
        """ Constructor for the BGProc object.

        Args:
            name (str): the name of the background process. this is derived
                from the name of the socket.
            sock (str): the path to the socket.
        """
        if not os.path.exists(sock):
            raise ValueError('The given socket ({}) must exist.'.format(sock))
        self.sock = sock
        self.name = name
        self.client = get_client(name)

        # register this instance with the manager.
        self.manager.add(self)

    def __str__(self):
        return '<BGProc: {} {}>'.format(self.name, self.sock)


BGProc.manager = ProcManager()


def get_proc(name):
    """ Get the background process model for the process with the
    given name.

    Args:
        name (str): the name of the background process.

    Returns:
        BGProc: the background process model associated with the
            given name.
        None: if the given name is not associated with a known background
            process.
    """
    return BGProc.manager.get(name)


def get_procs():
    """ Get all of the managed background processes.

    Yields:
        tuple: a tuple of process name and associated BGProc.
    """
    for k, v in BGProc.manager.processes.items():
        yield k, v
