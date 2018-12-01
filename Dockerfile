
FROM alpine 
# alpine is a lightweight Linux distribution

RUN apk add python3 libffi-dev openssl-dev python3-dev build-base
# install python3

COPY . . 

RUN python3 -m pip install --upgrade pip
# copy local files into the container
RUN python3 -m pip install -r src/requirements.txt 
# pip install requirements
EXPOSE 5000 
# expose port 5000

CMD python3 src/app.py 
# run the app

