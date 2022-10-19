FROM python:3.10

RUN useradd sandpiper -d /sandpiper \
 && mkdir /sandpiper \
 && chown sandpiper:sandpiper /sandpiper

WORKDIR /sandpiper
USER sandpiper
ENV PATH="/sandpiper/.local/bin:${PATH}"

RUN pip install --user --no-cache-dir \
    'Flask-CORS~=3.0.10' \
    'Flask-Migrate~=3.1.0' \
    'Flask-Script~=2.0.6' \
    'Flask-SQLAlchemy~=3.0.2' \
    'Flask~=2.2.2' \
    'uWSGI~=2.0.20' \
    'iso8601~=1.1.0' \
    'zenodo-backpack~=0.2.0' \
    git+https://github.com/wwood/singlem.git@v1.0.0beta2

COPY backend /sandpiper

CMD uwsgi --http :5000 --ini sandpiper.ini
# CMD flask run --host=0.0.0.0
