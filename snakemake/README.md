To run the prod, change the prod_config.yml to suit and then run:
```
~/git/sandpiper/snakemake$ pixi shell -e sandpiper

~/git/sandpiper/snakemake$ snakemake -c32 --profile aqua --configfile prod_config.yml
```

Test it works on HPC, then push the db and then push to code to GitHub so the deployment action runs.
