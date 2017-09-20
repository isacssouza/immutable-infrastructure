from troposphere import Template, Parameter, Ref, Output, GetAtt
from troposphere.cloudwatch import Alarm, MetricDimension
from troposphere.elasticloadbalancingv2 import Listener, \
    LoadBalancer, LoadBalancerAttributes, TargetGroup, Matcher, Action, \
    ListenerRule, Condition, TargetGroupAttribute

template = Template()


subnets = template.add_parameter(Parameter(
    'Subnets',
    Type='List<AWS::EC2::Subnet::Id>',
    Description=''
))

vpc_id = template.add_parameter(Parameter(
    'VpcId',
    Type='String',
    Description='The vpc to assign to the elb'
))

security_groups = template.add_parameter(Parameter(
    'SecurityGroups',
    Type='List<AWS::EC2::SecurityGroup::Id>',
    Description='List of security group ids to assign to the load balancer.'
))

sns_topic_arn = template.add_parameter(Parameter(
    'SnsTopicArn',
    Type='String',
    Description='Sns Topic Arn.'
))

load_balancer = template.add_resource(LoadBalancer(
    'ApplicationElasticLB',
    Name='api-elb',
    LoadBalancerAttributes=[
        LoadBalancerAttributes(Key='access_logs.s3.enabled', Value='false'),
        LoadBalancerAttributes(Key='idle_timeout.timeout_seconds', Value='60'),
    ],
    Scheme='internet-facing',
    SecurityGroups=Ref(security_groups),
    Subnets=Ref(subnets)
))

target_group = template.add_resource(TargetGroup(
    'DefaultTargetGroup',
    Name='api-default',
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

template.add_output(Output(
    'ElbName',
    Description='Logical ID of this the api load balancer.',
    Value=Ref(load_balancer)
))

template.add_output(Output(
    'TargetGroupArn',
    Description='Arn of the default target group.',
    Value=Ref(target_group)
))

print(template.to_json())
