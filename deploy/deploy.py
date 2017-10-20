from argparse import ArgumentParser
import subprocess
import boto3
import urllib2
import os
import time


def parse_args():
    parser = ArgumentParser(description='Deploy the application.')
    parser.add_argument('version', type=str, help='The version number for this deployment.')
    parser.add_argument('ami_id', type=str, help='Api AMI id to deploy.')
    return parser.parse_args()


def deploy(version, ami_id):
    print("Deploying version {} using {}.".format(version, ami_id))

    command = 'ansible-playbook '
    command += '-e "api_ami_id={}" '.format(ami_id)
    command += '-e "version={}" '.format(version)
    command += 'playbooks/deploy.yml'

    subprocess.call(command, shell=True)


def is_app(tags):
    return tags.get('Application') == 'true'


def is_version(tags, version):
    return tags.get('Version') == version


def to_tag_dict(tags):
    return {tag['Key']:  tag['Value'] for tag in tags}


def delete_old(new_version):
    client = boto3.client('cloudformation', region_name=os.environ['AWS_REGION'])

    all_stacks = client.describe_stacks()

    for stack in all_stacks['Stacks']:
        tags = to_tag_dict(stack['Tags'])
        if is_app(tags) and not is_version(tags, new_version):
            print('Deleting version {}.'.format(tags['Version']))
            client.delete_stack(StackName=stack['StackName'])


def delete_new(version):
    client = boto3.client('cloudformation', region_name=os.environ['AWS_REGION'])

    client.delete_stack(StackName='api-{}'.format(version))


def is_service_up(dns, tries=0, max_tries=10):
    url = 'http://{}/'.format(dns)
    print('GET {}'.format(url))

    success = False
    try:
        response = urllib2.urlopen(url)
        print('Service returned code: {}'.format(response.getcode()))
        success = response.getcode() == 200
    except urllib2.URLError as e:
        print('Failed to get url. Error: {}'.format(e))

    if not success and tries < max_tries:
        time.sleep(10)
        success = is_service_up(dns, tries + 1, max_tries)

    return success


def is_version_healthy(version):
    client = boto3.client('cloudformation', region_name=os.environ['AWS_REGION'])
    stacks = client.describe_stacks(StackName='api-{}'.format(version))
    stack = stacks['Stacks'][0]

    for output in stack['Outputs']:
        if output['OutputKey'] == 'ElbDns':
            dns = output['OutputValue']
            return is_service_up(dns)

    return False


def main():
    args = parse_args()
    version = args.version
    ami_id = args.ami_id

    deploy(version, ami_id)

    print('Version {} deployed.'.format(version))

    if is_version_healthy(version):
        print('New version is healthy, deleting old versions.')
        delete_old(version)
    else:
        print('New version is not healthy, deleting new version.')
        delete_new(version)


if __name__ == '__main__':
    main()
