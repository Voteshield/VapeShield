# Container image that runs your code
FROM public.ecr.aws/bitnami/python:3.10-prod

# build dependencies
#
ENV BUILD_PACKAGES="g++ libpq-dev curl git"

# Install build deps and heavy dependencies
#
RUN apt-get update
RUN apt-get install --no-install-recommends -y ${BUILD_PACKAGES}

# Environment values
#
ENV PYTHONUNBUFFERED=1 \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"


# prepend poetry and venv to path
ENV PATH="/opt/poetry/bin:/opt/pysetup/.venv/bin:$PATH"


# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=$POETRY_HOME python3 -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --no-dev


# Everything before this came from the Inspector

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY src/* /src/

WORKDIR /src

ENTRYPOINT [ "/opt/pysetup/.venv/bin/python" ]
CMD ["/opt/pysetup/.venv/bin/pytest", "-v", "/src/vape.py"]
