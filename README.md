This repository is the web front-end for the database of SingleM as applied to the SRA.

It is probably not useful on its own. Instead you might like to visit the website itself (https://sandpiper.qut.edu.au) or use the SingleM [code](https://github.com/wwood/singlem). It does contain some code for transforming SRA metadata into something more useful, though this is rather messy.

A separate repository https://github.com/wwood/public_sequencing_metadata_corrections contains manually collected corrections to metadata. These corrections are applied here for the sandpiper website.

# Dev on aqua

backend:
```
cd backend
pixi shell -e sandpiper
FLASK_ENV=development flask run --reload
```

frontend:
```
cd vue
pixi shell -e sandpiper
CHOKIDAR_USEPOLLING=1 SANDPIPER_TESTING=1 npm run dev -- --host 127.0.0.1
```
`CHOKIDAR_USEPOLLING=1` is needed on aqua to get file watching to work properly.

generating the test database:
```
cd snakemake_test
pixi run -e sandpiper snakemake --configfile test_config.yml
```
The Dropbox/sandpiper_dbs folder should contain the resulting duckdb database, so CI can download it from there.

Running unit tests, which tests both frontend and backend:
```
pixi run -e sandpiper pytest tests
```

# Testing for deployment

To ensure that the build process works, before release test that the following works. So far this has only been tested on b2, because docker is unavailable on aqua, which means the DB is unavailable and full testing cannot be done. But at least the containers should build.

First copy the test database to backend/db and name it as the current prod db is.
```
docker compose up
```

The server is then available on localhost:8000.

To mess around with it, you might do something like this to e.g. force rebuild of the web, and then deploy locally:
```
docker compose build web && docker compose up
```

# Deployment
```
./release --version 1.0.0 --gtdb-version R226 --scrape-date '20 Feb, 2025'
```
Then follow instructions. Note also there is a `--tag-version` to disentangle the deploy from the actual version if needed. Note, the tag number must increase, otherwise it doesn't get deployed.
