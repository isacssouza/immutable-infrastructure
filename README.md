## Build pipeline for immutable infrastructure

This project demonstrates a fully automated Continuous Integration environment for a simple HTTP API that is 
built, baked into a machine image and deployed to AWS. At the end of the build pipeline, a new Elastic Load
Balancer and Auto Scaling Group is deployed to AWS and serves the API endpoint.

This project has four main modules:
 - api: a maven project with a Java Hello World HTTP endpoint
 - packer: scripts to bake machine images that run the api
 - deploy: ansible scripts to deploy the machine images to AWS
 - jenkins: a docker file and Jenkins jobs with a CI/CD environment
 
### API

The api module is a very simple Spring Boot Java application with an HTTP endpoint that returns "Hello, World!".
The maven build outputs a JAR file that is used as input to bake a machine image.

### Packer

The packer module contains packer templates to bake a machine image that runs the API JAR created by the maven project.
It uses the [packer](https://www.packer.io/) tool to start an AWS EC2 instance, configure it with the API and create an AMI.

### Deploy

The deploy module contains an [Ansible](https://www.ansible.com/) structure to deploy 
[AWS Cloud Formation](https://aws.amazon.com/cloudformation/) templates that will create the necessary infrastructure to run
the API server in an Auto Scaling Group and behind an Elastic Load Balancer.

The Cloud Formation templates are created using the [Troposphere](https://github.com/cloudtools/troposphere) python library.

### Jenkins

The [Jenkins](https://jenkins.io/) module contains a [Docker](https://www.docker.com/) container that runs a Jenkins pipeline
that builds, bakes and deploys the API to AWS.
