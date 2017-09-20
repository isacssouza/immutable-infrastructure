from troposphere import Output, Ref, Template, Parameter
from troposphere.sns import Topic, SubscriptionResource


template = Template(Description='Creates a new SNS Topic')

email = template.add_parameter(Parameter(
    'Email',
    Type='String'
))

topic = template.add_resource(Topic(
    'SnsTopic',
    DisplayName='sns-topic',
    TopicName='sns-topic'
))

template.add_resource(SubscriptionResource(
    'Subscription',
    Protocol='email',
    Endpoint=Ref(email),
    TopicArn=Ref(topic)
))

template.add_output(Output(
    'TopicArn',
    Description='SNS Topic ARN',
    Value=Ref(topic)
))

print(template.to_json())
