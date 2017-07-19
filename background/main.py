#!/usr/bin/env python
""" Main component of the background sensor read process.

    Author: Erick Daniszewski
    Date:   18 July 2017

    \\//
     \/apor IO
"""

import hub


def main():
    """ Main entrypoint for the background sensor reads.
    """
    with hub.Hub(debug=True) as sensor_hub:

        data = sensor_hub.read_differential_pressure()
        print data


if __name__ == '__main__':
    main()
