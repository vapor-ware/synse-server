# graphql-frontend

## Kick the tires

Note: the default configuration uses `demo.vapor.io`. If you'd like to use a different backend, check out `--help`.

### From the web

    make run

At this point there is an interactive terminal running that you can do interactive queries with. Send your browser to `http://localhost:5001/graphql` and play around. Click the `Docs` tab on the right for the schema or go to `tests/queries/` to look at some example queries.

### From the command line

    make dev
    python runserver.py &
    ./bin/query --list
    ./bin/query test_racks
    ./bin/query --help

## Development

### Run the server

    make dev
    python runserver.py

- From outside the container (or inside it), you can run `curl localhost:5001`

### Run the tests (as part of development)

1. Run the tests

    make dev
    make one test="-a now"`

See [nosetests](http://nose.readthedocs.io/en/latest/usage.html) for some more examples. Adding `@attr('now')` to the top of a function is a really convenient way to just run a single test.

### Getting isort errors?

- See the changes:

    isort graphql_frontend tests -rc -vb --dont-skip=__init_.py --diff

- Atomic updates:

    isort graphql_frontend tests -rc -vb --dont-skip=__init_.py --atomic

## Testing (run the whole suite)

- Tests assume a running, emulated synse-server on the same host. It uses `localhost` to talk to the router. If this you'd like to use a different synse-server, change the config.
- `make test`
