FROM jenkins:latest

USER root

# install plugins
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt

# setup job that will create other jobs
COPY seed-job.xml /usr/share/jenkins/ref/jobs/create-jobs/config.xml

# prevent initial setup screen
RUN echo 2.60.3 > /usr/share/jenkins/ref/jenkins.install.UpgradeWizard.state
RUN echo 2.60.3 > /usr/share/jenkins/ref/jenkins.install.InstallUtil.lastExecVersion
RUN echo '!Jenkins123*' /usr/share/jenkins/ref/secrets/initialAdminPassword

# install additional tools
RUN apt-get update && apt-get install -y python-virtualenv

RUN wget -nv 'https://releases.hashicorp.com/packer/1.1.0/packer_1.1.0_linux_amd64.zip' -O /tmp/packer.zip
RUN unzip /tmp/packer.zip -d /bin

RUN wget -nv 'https://get.docker.com/builds/Linux/x86_64/docker-1.13.1.tgz' -O /docker.tgz
RUN tar xzf /docker.tgz docker/docker
RUN mv docker/docker /usr/bin/
RUN chmod +x /usr/bin/docker