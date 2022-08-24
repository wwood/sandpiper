This repository is the web front-end for the database of SingleM as applied to the SRA.

It is probably not useful on its own. Instead you might like to visit the website itself (https://sandpiper.qut.edu.au) or use the SingleM [code](https://github.com/wwood/singlem). It does contain some code for transforming SRA metadata into something more useful, though this is rather messy.

A separate repository https://github.com/wwood/public_sequencing_metadata_corrections contains manually collected corrections to metadata. These corrections are applied here for the sandpiper website.

# Setup

```
docker-compose up
```

The server is then available on localhost:8000.
