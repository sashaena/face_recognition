FROM alpine


RUN apk update && apk upgrade && apk add --update python python-dev py-pip bash
RUN apk add nano
WORKDIR /app
#ADD requirements.txt /app
RUN pip install flask requests
EXPOSE 5000

ENTRYPOINT ["/bin/bash"]

