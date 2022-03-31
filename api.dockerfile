FROM python:3.8

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
    'Flask-SQLAlchemy~=2.5.1' \
    'Flask~=2.1.1' \
    'uWSGI~=2.0.20' \
    # seems to be running from dev branch
    git+https://github.com/wwood/singlem.git@dev

COPY backend /sandpiper

# CMD uwsgi --ini sandpiper.ini
CMD flask run --host=0.0.0.0
