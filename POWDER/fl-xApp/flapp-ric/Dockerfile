FROM python:3.10-alpine

# copy rmr libraries from builder image in lieu of an Alpine package
COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.6.0 /usr/local/lib64/librmr* /usr/local/lib64/
# RMR setup
RUN mkdir -p /opt/route/
COPY test_route.rt /opt/route/test_route_RIC.rt
COPY init/flapp-config.json /opt/config/flapp-config.json
ENV LD_LIBRARY_PATH /usr/local/lib/:/usr/local/lib64
ENV RMR_SEED_RT /opt/route/test_route_RIC.rt
RUN ip=$(hostname -i)
ENV RMR_SRC_ID $ip
# ENV CONFIG_FILE /opt/config/flapp-config.json

# sdl needs gcc
RUN apk update && apk add gcc musl-dev bash

# Install
RUN pip3 install pip --upgrade
RUN pip install tensorflow 
RUN pip install ricxappframe 
RUN pip3 install setuptools
RUN pip3 install wheel
RUN pip3 install numpy 
# RUN pip3 install scikit-learn 
COPY fl_ric.py .

# Run
ENV PYTHONUNBUFFERED 1
CMD python fl_ric.py