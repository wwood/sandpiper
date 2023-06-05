To run the prod, change the prod_config.yml to suit and then run:
```
$ conda activate sandpiper-dev #built from ../sandpiper.yml

$ PYTHONPATH=~/git/singlem PATH=~/git/kingfisher/bin:$PATH notify snakemake -c1 --use-conda --configfile prod_config.yml
```

Test it works on HPC, then push the db and then push to code to GitHub so the deployment action runs.
