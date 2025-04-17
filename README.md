This repository is the web front-end for the database of SingleM as applied to the SRA.

It is probably not useful on its own. Instead you might like to visit the website itself (https://sandpiper.qut.edu.au) or use the SingleM [code](https://github.com/wwood/singlem). It does contain some code for transforming SRA metadata into something more useful, though this is rather messy.

A separate repository https://github.com/wwood/public_sequencing_metadata_corrections contains manually collected corrections to metadata. These corrections are applied here for the sandpiper website.

# Dev on lyra

backend:
```
cd backend
pixi shell -e sandpiper
FLASK_ENV=development flask run --reload
```

frontend:
```
cd vue
pixi run -e sandpiper API_URL=localhost:5000 npm run serve -- --host localhost
```

# Testing for deplyment

To ensure that the build process works, before release test that the following works. So far this has only been tested on b2, because docker is available on aqua, which means the DB is unavailable and full testing cannot be done. But at least the containers should build.

```
docker-compose up
```

The server is then available on localhost:8000.

# Deployment
```
./release --version 1.0.0 --gtdb-version R226 --scrape-date '20 Feb, 2025'
```
Then follow instructions.
