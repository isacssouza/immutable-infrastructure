FROM jenkins:latest

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
COPY seed-job.xml /usr/share/jenkins/ref/jobs/create-jobs/config.xml

RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt
RUN echo 2.60.3 > /usr/share/jenkins/ref/jenkins.install.UpgradeWizard.state
RUN echo 2.60.3 > /usr/share/jenkins/ref/jenkins.install.InstallUtil.lastExecVersion
RUN echo '!Jenkins123*' /usr/share/jenkins/ref/secrets/initialAdminPassword