ARG PYTHON_BASE=3.13-slim
# build stage
FROM python:$PYTHON_BASE AS builder

# install PDM
RUN pip install -U pdm
# disable update check
ENV PDM_CHECK_UPDATE=false
# copy filesº
COPY pyproject.toml pdm.lock readme.md /project/
COPY src/ /project/src

# install dependencies and project into the local packages directory
WORKDIR /project
RUN pdm install --check --prod --no-editable

# run stage
FROM python:$PYTHON_BASE
RUN apt-get update -y && apt-get install -y git
# retrieve packages from build stage
COPY --from=builder /project/.venv/ /project/.venv
ENV PATH="/project/.venv/bin:$PATH"
# set command/entrypoint, adapt to fit your needs
COPY src /project/src
WORKDIR /workdir
ENTRYPOINT [ "python", "/project/src/main.py" ]
CMD ["python", "/project/src/main.py"]
LABEL org.opencontainers.image.source = "https://github.com/poble9digital/odoo_addon_manager"
