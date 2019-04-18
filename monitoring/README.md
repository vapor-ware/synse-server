# Synse Server Application Monitoring
This sample deployment sets up Synse Server, Prometheus, and Grafana to provide a dashboard for
application monitoring for Synse Server.

To run, simply:
```
docker-compose up -d
```

All service endpoints are accessible locally:
- **Synse Server**: `localhost:5000`
- **Prometheus**: `localhost:9090`
- **Grafana**: `localhost:3000`

The login for the Grafana dashboard at `localhost:3000` is `admin`/`admin`. Once logged in,
you can select the "Synse Server Application Metrics" dashboard. To get data, you will need
to hit Synse Server endpoints, e.g.

- `localhost:5000/test`
- `localhost:5000/version`
- `localhost:5000/v3/config`
- `localhost:5000/v3/plugin`
- `localhost:5000/v3/scan`
- ...
