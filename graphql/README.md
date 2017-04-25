# graphql-frontend

## Kick the tires

Note: the default configuration uses `demo.vapor.io` and uses OpenDCRE instead of core. If you'd like to use a different backend (or mode), check out `--help`.

### From the web

    make build run

At this point there is an interactive terminal running that you can do interactive queries with. Send your browser to `http://localhost:5001/graphql` and play around. Click the `Docs` tab on the right for the schema or go to `tests/queries/` to look at some example queries.

### From the command line

    make build dev
    python runserver.py &
    ./query.py --list
    ./query.py test_racks
    ./query.py --help

## Development

### Run the server

    make build dev
    python runserver.py

- From outside the container (or inside it), you can run `curl localhost:5001`

### Run the tests (as part of development)

First, start aws-core locally:

    cd aws-core
    make run-e2e-multicluster-x64

Then, run the tests:

    make build dev
    make one test="-a now"`

See [nosetests](http://nose.readthedocs.io/en/latest/usage.html) for some more examples. Adding `@attr('now')` to the top of a function is a really convenient way to just run a single test.

### Getting isort errors?

- See the changes:

    isort graphql_frontend tests -rc -vb --dont-skip=__init_.py --diff

- Atomic updates:

    isort graphql_frontend tests -rc -vb --dont-skip=__init_.py --atomic

## Testing (run the whole suite)

- Tests assume a running `aws-core` installation on the same host. It uses `localhost` to talk to the router. If this isn't where you're running it, change the config.
- `make test`
