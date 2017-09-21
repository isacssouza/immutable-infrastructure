from troposphere import Ref, Parameter, Template
from troposphere.autoscaling import LaunchConfiguration, AutoScalingGroup

template = Template()

security_group = template.add_parameter(Parameter(
    "SecurityGroup",
    Type="String",
    Description="Security group for api instances.",
))

key_name = template.add_parameter(Parameter(
    "KeyName",
    Type="String",
    Description="Name of an existing EC2 KeyPair to enable SSH access",
    MinLength="1",
    AllowedPattern="[\x20-\x7E]*",
    MaxLength="255",
    ConstraintDescription="can contain only ASCII characters.",
))

ami_id = template.add_parameter(Parameter(
    "AmiId",
    Type="String",
    Description="The AMI id for the api instances",
))

instance_type = template.add_parameter(Parameter(
    "InstanceType",
    Type="String",
    Description="Instance type for api instances.",
))

desired_capacity = template.add_parameter(Parameter(
    "DesiredCapacity",
    Default="1",
    Type="String",
    Description="Number of desired api servers to run",
))

max_size = template.add_parameter(Parameter(
    "MaxSize",
    Default="3",
    Type="String",
    Description="Maximum number of api servers to run",
))

min_size = template.add_parameter(Parameter(
    "MinSize",
    Default="1",
    Type="String",
    Description="Minimum number of api servers to run",
))

target_group = template.add_parameter(Parameter(
    "TargetGroupArn",
    Type="String",
    Description="Arn of a target group to register the instances",
))

subnets = template.add_parameter(Parameter(
    'Subnets',
    Type='List<AWS::EC2::Subnet::Id>',
    Description='Subnets for the auto scaling group.'
))

launch_config = template.add_resource(LaunchConfiguration(
    "LaunchConfiguration",
    ImageId=Ref(ami_id),
    KeyName=Ref(key_name),
    SecurityGroups=[Ref(security_group)],
    InstanceType=Ref(instance_type),
))

auto_scaling_group = template.add_resource(AutoScalingGroup(
    "AutoscalingGroup",
    LaunchConfigurationName=Ref(launch_config),
    DesiredCapacity=Ref(desired_capacity),
    MinSize=Ref(min_size),
    MaxSize=Ref(max_size),
    VPCZoneIdentifier=Ref(subnets),
    TargetGroupARNs=[Ref(target_group)]
))

print(template.to_json())
