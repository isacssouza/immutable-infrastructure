from troposphere import Ref, Template, Parameter, Output
from troposphere.ec2 import SecurityGroup, SecurityGroupRule

template = Template()

vpc_id = template.add_parameter(Parameter(
    'VpcId',
    Type='AWS::EC2::VPC::Id',
    Description='The Vpc Id.'
))

api_elb_sg = template.add_resource(SecurityGroup(
    'ApiElbSg',
    VpcId=Ref(vpc_id),
    GroupDescription='Security group for the api ELB',
    SecurityGroupIngress=[SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="80",
        ToPort="80",
        CidrIp="0.0.0.0/0",
    )]
))

api_sg = template.add_resource(SecurityGroup(
    'ApiSg',
    VpcId=Ref(vpc_id),
    GroupDescription='Security Group for the api',
    SecurityGroupIngress=[
        SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="8080",
            ToPort="8080",
            SourceSecurityGroupId=Ref(api_elb_sg),
        ),
        SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="22",
            ToPort="22",
            CidrIp='0.0.0.0/0',
        )]
))

template.add_output(Output(
    'ApiElbSgId',
    Description='Security group id for the api ELB',
    Value=Ref(api_elb_sg)
))

template.add_output(Output(
    'ApiSgId',
    Description='Security group id for the api',
    Value=Ref(api_sg)
))

print(template.to_json())
