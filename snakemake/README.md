To run the prod, change the prod_config.yml to suit and then run:
```
~/git/sandpiper/snakemake$ pixi run -e sandpiper snakemake --resources ncbi_api=1 -c32 --profile --configfile prod_config.yml
```

Test it works on HPC, then push the db and then push to code to GitHub so the deployment action runs.
