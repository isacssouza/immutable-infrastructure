from troposphere import Template, Parameter, Ref, Output, GetAtt, Join
from troposphere.cloudwatch import Alarm, MetricDimension
from troposphere.elasticloadbalancingv2 import Listener, \
    LoadBalancer, LoadBalancerAttributes, TargetGroup, Matcher, Action, \
    ListenerRule, Condition, TargetGroupAttribute
from troposphere.ec2 import SecurityGroup, SecurityGroupRule
from troposphere.autoscaling import LaunchConfiguration, AutoScalingGroup

template = Template()

vpc_id = template.add_parameter(Parameter(
    'VpcId',
    Type='String',
    Description='The vpc to assign to the elb'
))

sns_topic_arn = template.add_parameter(Parameter(
    'SnsTopicArn',
    Type='String',
    Description='Sns Topic Arn.'
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

subnets = template.add_parameter(Parameter(
    'Subnets',
    Type='List<AWS::EC2::Subnet::Id>',
    Description='Subnets for the auto scaling group.'
))

version = template.add_parameter(Parameter(
    "Version",
    Type="String",
    Description="The version of the api",
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

load_balancer = template.add_resource(LoadBalancer(
    'ApplicationElasticLB',
    Name=Join('-', ['api', 'elb', Ref(version)]),
    LoadBalancerAttributes=[
        LoadBalancerAttributes(Key='access_logs.s3.enabled', Value='false'),
        LoadBalancerAttributes(Key='idle_timeout.timeout_seconds', Value='60'),
    ],
    Scheme='internet-facing',
    SecurityGroups=[Ref(api_elb_sg)],
    Subnets=Ref(subnets)
))

target_group = template.add_resource(TargetGroup(
    'DefaultTargetGroup',
    Name=Join('-', ['api', 'default', Ref(version)]),
    HealthCheckIntervalSeconds=5,
    HealthCheckProtocol='HTTP',
    HealthCheckTimeoutSeconds=2,
    HealthCheckPath='/',
    HealthyThresholdCount=2,
    UnhealthyThresholdCount=3,
    Matcher=Matcher(HttpCode='200'),
    Port=8080,
    Protocol='HTTP',
    TargetGroupAttributes=[
        TargetGroupAttribute(Key='deregistration_delay.timeout_seconds', Value='120')
    ],
    VpcId=Ref(vpc_id)
))

listener = template.add_resource(Listener(
    'HttpListener',
    Port=80,
    Protocol='HTTP',
    LoadBalancerArn=Ref(load_balancer),
    DefaultActions=[Action(
        Type="forward",
        TargetGroupArn=Ref(target_group)
    )]
))

template.add_resource(ListenerRule(
    'ListenerRule',
    ListenerArn=Ref(listener),
    Conditions=[Condition(Field='path-pattern', Values=['*'])],
    Actions=[Action(
        Type='forward',
        TargetGroupArn=Ref(target_group)
    )],
    Priority=1000
))

target_group_dimension = GetAtt(target_group, 'TargetGroupFullName')
load_balancer_dimension = GetAtt(load_balancer, 'LoadBalancerFullName')
template.add_resource(Alarm(
    'LowHealthyHostsAlarm',
    ActionsEnabled=True,
    AlarmActions=[Ref(sns_topic_arn)],
    OKActions=[Ref(sns_topic_arn)],
    InsufficientDataActions=[Ref(sns_topic_arn)],
    AlarmDescription='Alarm for checking if healthy hosts falls below one',
    ComparisonOperator='LessThanThreshold',
    Dimensions=[
        MetricDimension(
            Name='TargetGroup',
            Value=target_group_dimension
        ),
        MetricDimension(
            Name='LoadBalancer',
            Value=load_balancer_dimension
        )
    ],
    EvaluationPeriods=1,
    MetricName='HealthyHostCount',
    Namespace='AWS/ApplicationELB',
    Period=60,
    Statistic='Average',
    Threshold='1',
    Unit='Count'
))

template.add_resource(Alarm(
    'HighAverageLatencyAlarm',
    ActionsEnabled=True,
    AlarmActions=[Ref(sns_topic_arn)],
    OKActions=[Ref(sns_topic_arn)],
    InsufficientDataActions=[Ref(sns_topic_arn)],
    AlarmDescription='Alarm for checking average request latency',
    ComparisonOperator='GreaterThanOrEqualToThreshold',
    Dimensions=[
        MetricDimension(
            Name='TargetGroup',
            Value=target_group_dimension
        ),
        MetricDimension(
            Name='LoadBalancer',
            Value=load_balancer_dimension
        )
    ],
    EvaluationPeriods=1,
    MetricName='TargetResponseTime',
    Namespace='AWS/ApplicationELB',
    Period=60,
    Statistic='Average',
    Threshold='1.000',
    Unit='Seconds'
))

template.add_resource(Alarm(
    'High5XXResponseAlarm',
    ActionsEnabled=True,
    AlarmActions=[Ref(sns_topic_arn)],
    OKActions=[Ref(sns_topic_arn)],
    AlarmDescription='Alarm for checking number of 5XX responses',
    ComparisonOperator='GreaterThanOrEqualToThreshold',
    Dimensions=[
        MetricDimension(
            Name='TargetGroup',
            Value=target_group_dimension
        ),
        MetricDimension(
            Name='LoadBalancer',
            Value=load_balancer_dimension
        )
    ],
    EvaluationPeriods=1,
    MetricName='HTTPCode_Target_5XX_Count',
    Namespace='AWS/ApplicationELB',
    Period=60,
    Statistic='Sum',
    Threshold='5',
    Unit='Count'
))

launch_config = template.add_resource(LaunchConfiguration(
    "LaunchConfiguration",
    ImageId=Ref(ami_id),
    KeyName=Ref(key_name),
    SecurityGroups=[Ref(api_sg)],
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

template.add_output(Output(
    'ElbDns',
    Description='Dns of the api load balancer.',
    Value=GetAtt(load_balancer, 'DNSName')
))

template.add_output(Output(
    'ElbName',
    Description='Logical ID of the api load balancer.',
    Value=Ref(load_balancer)
))

template.add_output(Output(
    'TargetGroupArn',
    Description='Arn of the default target group.',
    Value=Ref(target_group)
))

print(template.to_json())
