# aws-terminate-untagged-instances
A simple python serverless lambda function which would terminate all EC2 instances which don’t follow a tagging criteria. (A free tier AWS account would work). 

### AWS Services used
- SES
- EC2
- Lambda 
- DynamoDB 
- EventBridge 

### Deployment Steps:
- Create a lambda function terminate-untagged-instances
![Lambda function setup](images/lambda_function.jpg)

#### Configuration
- Go to Configuration > General Configuration > Increase timeout to 1 min.
- Go to Configuration > Permissions > Execution Role
    - Add below policies to the role
    ![Role setup](images/role.jpg)

- Create a dynamoDB table terminate-untagged-instances with partition key - instanceId (String) 
- Create a EventBridge rule to schedule the lambda function every 1 hour.


