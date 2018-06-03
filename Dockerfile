FROM centos:7.0.1406
RUN yum swap -y fakesystemd systemd && \
    yum install -y python-setuptools systemd-devel mysql-connector-python mysql-devel gcc python-devel
RUN easy_install pip
RUN mkdir /opt/flask_blog
WORKDIR /opt/flask_blog
ADD requirements.txt /opt/flask_blog
RUN pip install -r requirements.txt
ADD . /opt/flask_blog
