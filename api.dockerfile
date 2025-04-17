FROM python:3.10

RUN useradd sandpiper -d /sandpiper \
 && mkdir /sandpiper \
 && chown sandpiper:sandpiper /sandpiper

WORKDIR /sandpiper
USER sandpiper
ENV PATH="/sandpiper/.local/bin:${PATH}"

# flask-sqlalchemy          3.0.3              pyhd8ed1ab_0    conda-forge
# sqlalchemy                1.4.49          py311h459d7ec_0    conda-forge
# (sandpiper-dev2)cl5n007:20230712:~/git/sandpiper/backend$ conda list |grep flask
# flask                     2.3.2              pyhd8ed1ab_0    conda-forge
# flask-cors                4.0.0              pyhd8ed1ab_0    conda-forge
# flask-migrate             4.0.4              pyhd8ed1ab_0    conda-forge
# flask-script              2.0.6                      py_0    conda-forge
# flask-sqlalchemy          3.0.3              pyhd8ed1ab_0    conda-forge

RUN pip install --user --no-cache-dir \
    'Flask-CORS~=4.0.0' \
    'Flask-Migrate~=4.0.4' \
    'Flask-Script~=2.0.6' \
    'Flask-SQLAlchemy~=3.0.3' \
    'Flask~=2.3.2' \
    'uWSGI~=2.0.20' \
    'iso8601~=1.1.0' \
    'zenodo-backpack~=0.2.0' \
    'sqlalchemy~=1.4.49' \
    'polars~=1.5.0' \
    # Up to date singlem requires sqlalchemy 2.0, but haven't migrated sandpiper yet
    git+https://github.com/wwood/singlem.git@v1.0.0beta2

COPY backend /sandpiper

CMD uwsgi --http :5000 --ini sandpiper.ini
# CMD flask run --host=0.0.0.0
