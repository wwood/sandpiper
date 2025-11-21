
FROM python:3.12

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
    'Flask-CORS~=5.0.1' \
    'Flask-Migrate~=4.1.0' \
    'Flask-Script~=2.0.6' \
    'Flask-SQLAlchemy~=3.1.1' \
    'Flask~=3.1.0' \
    'uWSGI~=2.0.31' \
    'iso8601~=2.1.0' \
    'zenodo-backpack~=0.3.1' \
    'sqlalchemy~=2.0.40' \
    'polars~=1.26.0' \
    # Are dependencies of singlem actually needed? eh.
    'singlem~=0.18.1'
RUN pip install --user --no-cache-dir \
    'duckdb-engine~=0.15.0' \
    'duckdb~=1.3.2'


COPY backend /sandpiper

CMD uwsgi --http :5000 --ini sandpiper.ini
# CMD flask run --host=0.0.0.0
