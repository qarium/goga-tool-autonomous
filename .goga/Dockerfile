FROM qarium/goga-python-3.14:2.0

USER root

COPY . /tmp/project
RUN cd /tmp/project && goga install && goga install --local /tmp/project:autonomous && rm -rf /tmp/project

USER goga
