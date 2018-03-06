from troposphere import Template, Ref, Parameter, Select, Output, GetAZs
from troposphere.ec2 import VPC, Subnet, InternetGateway, RouteTable, Route, \
    SubnetRouteTableAssociation, VPCGatewayAttachment

VPC_LOGICAL_NAME = 'Vpc'


template = Template()

region = Ref('AWS::Region')
account = Ref('AWS::AccountId')

vpc_ip_range = template.add_parameter(Parameter(
    'VpcIpRange',
    Type='String',
    Default='192.168.0.0/16'
))

subnet_ip_ranges = template.add_parameter(Parameter(
    'SubnetIpRanges',
    Type='CommaDelimitedList',
    Default='192.168.0.0/23, 192.168.2.0/23, 192.168.4.0/23'
))

vpc = template.add_resource(VPC(
    VPC_LOGICAL_NAME,
    CidrBlock=Ref(vpc_ip_range),
    EnableDnsSupport=True,
    EnableDnsHostnames=True,
    InstanceTenancy='default'
))

internet_gateway = template.add_resource(InternetGateway('InternetGateway'))

template.add_resource(VPCGatewayAttachment(
    'VpcGatewayAttachment',
    InternetGatewayId=Ref(internet_gateway),
    VpcId=Ref(vpc)
))

for idx in range(0, 3):
    zone = Select(idx, GetAZs(region))
    subnet = template.add_resource(Subnet(
        'Subnet{}'.format(idx),
        AvailabilityZone=zone,
        CidrBlock=Select(idx, Ref(subnet_ip_ranges)),
        MapPublicIpOnLaunch=True,
        VpcId=Ref(vpc)
    ))

    template.add_output(Output(
        'SubnetId{}'.format(idx),
        Description='{} Subnet Id'.format(zone),
        Value=Ref(subnet)
    ))

    route_table = template.add_resource(RouteTable(
        'RouteTable{}'.format(idx),
        VpcId=Ref(vpc)
    ))

    template.add_resource(Route(
        'InternetRoute{}'.format(idx),
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=Ref(internet_gateway),
        RouteTableId=Ref(route_table)
    ))

    template.add_resource(SubnetRouteTableAssociation(
        'RouteAssociation{}'.format(idx),
        RouteTableId=Ref(route_table),
        SubnetId=Ref(subnet)
    ))

    template.add_output(Output(
        'SubnetAz{}'.format(idx),
        Description='Subnet Availability Zone',
        Value=zone
    ))


template.add_output(Output(
    'VpcId',
    Description='Vpc Id',
    Value=Ref(vpc)
))

print(template.to_json())
