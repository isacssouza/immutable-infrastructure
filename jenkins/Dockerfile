FROM jenkins:latest

USER root

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
COPY seed-job.xml /usr/share/jenkins/ref/jobs/create-jobs/config.xml

RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt
RUN echo 2.60.3 > /usr/share/jenkins/ref/jenkins.install.UpgradeWizard.state
RUN echo 2.60.3 > /usr/share/jenkins/ref/jenkins.install.InstallUtil.lastExecVersion
RUN echo '!Jenkins123*' /usr/share/jenkins/ref/secrets/initialAdminPassword

RUN wget -nv 'https://releases.hashicorp.com/packer/1.1.0/packer_1.1.0_linux_amd64.zip' -O /tmp/packer.zip
RUN unzip /tmp/packer.zip -d /bin

RUN wget -nv 'https://get.docker.com/builds/Linux/x86_64/docker-1.13.1.tgz' -O /tmp/docker.tgz
RUN tar -C /usr/bin/ xzf /tpm/docker.tgz docker/docker.tgz