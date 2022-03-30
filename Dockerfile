# FROM ubuntu:20.04

# RUN apt update && apt dist-upgrade -y

# ADD sandpiper /sandpiper

# RUN apt install npm -y

FROM nginx

RUN apt update

RUN apt install wget -y

ENV MINICONDA_VERSION latest
ENV CONDA_DIR $HOME/miniconda3
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-$MINICONDA_VERSION-Linux-x86_64.sh -O ~/miniconda.sh && \
    chmod +x ~/miniconda.sh && \
    ~/miniconda.sh -b -p $CONDA_DIR && \
    rm ~/miniconda.sh
ENV PATH=$CONDA_DIR/bin:$PATH
RUN echo ". $CONDA_DIR/etc/profile.d/conda.sh" >> ~/.profile

RUN apt install python2-minimal -y
# RUN which -a python3
RUN apt install build-essential -y

RUN conda install -c base -c conda-forge mamba

RUN mkdir /sandpiper
ADD vue /sandpiper/vue
ADD backend /sandpiper/backend
ADD sandpiper.yml /sandpiper/sandpiper.yml
RUN cd /sandpiper && mamba env update -p ${CONDA_DIR} -f sandpiper.yml

RUN cd /sandpiper/vue && npm install -g --production
# RUN cd /sandpiper/vue && npm install -g --production @vue/cli-service @vue/cli-plugin-babel @vue/cli-plugin-eslint @vue/cli-plugin-router @vue/cli-plugin-typescript @vue/cli-plugin-vuex
# RUN cd /sandpiper/vue && npm install -g --production vue-cli-plugin-buefy
# RUN cd /sandpiper/vue && npm run build


# Next get nginx setup?