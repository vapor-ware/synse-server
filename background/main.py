#!/usr/bin/env python
""" Main component of the background sensor read process.

    Author: Erick Daniszewski
    Date:   18 July 2017

    \\//
     \/apor IO
"""

import datetime

import hub


def main():
    """ Main entry point for the background sensor reads.
    """
    with hub.Hub(debug=True) as sensor_hub:

        # reference time - this is used to determine when to read the temp/humidity
        # and airflow/temp sensors. see comment below for more context.
        ref_time = None

        _done = False
        while not _done:

            ts, data = sensor_hub.read_differential_pressure()
            print '---- differential pressure ----'
            print ts
            print data

            ts, data = sensor_hub.read_thermistors()
            print '---- thermistors ----'
            print ts
            print data

            # since the CEC sensor hub only updates the humidity, airflow and
            # temperature every second, there is no need to keep reading it out
            # every loop iteration. instead, we do a read every second, based on
            # the `ref_time` variable.
            now = datetime.datetime.utcnow()
            if ref_time is None or (now - ref_time).total_seconds() >= 1:
                ref_time = now

                ts, data = sensor_hub.read_temp_humidity()
                print '---- humidity / temperature ----'
                print ts
                print data

                ts, data = sensor_hub.read_air_speed_temp()
                print '---- air speed / temperature ----'
                print ts
                print data

            # fixme -- for now, just break out after the first iteration.
            _done = True


if __name__ == '__main__':
    main()
