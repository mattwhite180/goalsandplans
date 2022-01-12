FROM jenkins/jenkins:2.319.1-jdk11

ENV TZ="America/Denver"

USER root

RUN apt-get update && apt-get install -y lsb-release python3 python3-pip sudo

RUN echo "jenkins ALL=NOPASSWD: ALL" >> /etc/sudoers

RUN curl -fsSLo /usr/share/keyrings/docker-archive-keyring.asc \
  https://download.docker.com/linux/debian/gpg

RUN echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/usr/share/keyrings/docker-archive-keyring.asc] \
  https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list

RUN apt-get update && apt-get install -y docker-ce-cli

RUN pip3 install --upgrade pip setuptools wheel
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

USER jenkins

#COPY plugins.txt /usr/share/jenkins/plugins.txt
#RUN /usr/local/bin/plugins.sh /usr/share/jenkins/plugins.txt

COPY jenkinsfile .
COPY seleniumtest.py .

RUN jenkins-plugin-cli --plugins "blueocean:1.25.2 docker-workflow:1.26"