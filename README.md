# Givenergy InfluxDB Updater

Utility to poll [Givenergy](https://givenergy.cloud) API periodically and push the current data to [InfluxDB](https://influxdata.com).

## Configuration

The simplest way to run this is with `docker-compose`. Put your Givenergy API token in the environment variable `GIVENERGY_API_TOKEN` and `docker-compose up --build`. This uses fixed and not very secure credentials for influxdb.

If you need to secure influxdb better, or already have an instance running just
run the script directly or build its Docker image. It will read the following
environment variables:

* `GIVENERGY_API_TOKEN`
* `INFLUX_TOKEN`
* `INFLUX_URL`

Your can specify `--org <organisation>` and `--bucket <bucket>` on the script or docker command lines. These are used when writing to InfluxDB.

`--period <seconds>` adjusts the polling period. The default is five minutes, which is how often the Givenergy API updates.
