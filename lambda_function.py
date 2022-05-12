import json
import boto3
import datetime

# Configure to add more tags
tagstoCheck = ["Name", "Environment"]

# Email Subject
subject = "Alert! Instance: {0} running without proper tags"
# Email Message
message = "Missing tags:{0}, the instance will be terminated in 6 hours."

# Instance Termination Email Subject
termination_subject = (
    "Alert! Instance: {0} running without proper tags has been terminated"
)

# DynamoDB table to store email logs
table = "terminate-untagged-instances"

ec2 = boto3.resource("ec2")
ec2client = boto3.client("ec2")
dynamodb = boto3.client("dynamodb")
ses = boto3.client("ses")

from utilities import (
    sendEmail,
    checkEmptyTags,
    getMissingTags,
    createTagsifEmpty,
    checkEmailSent,
    getEmailAddr,
    logEmailTime,
    deleteLogs,
    getTimeDifference,
)


def lambda_handler(event, context):
    # TODO implement
    instances = ec2client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["pending", "running"]}]
    )

    for reservation in instances["Reservations"]:
        for instance in reservation["Instances"]:

            instance_id = instance["InstanceId"]

            # If tags do not exist, create them
            createTagsifEmpty(instance)

            # Instance contains the empty tags
            if checkEmptyTags(instance):
                print("Empty Tags for instance_id:" + instance_id)

                # Email Notification is already sent
                if checkEmailSent(instance_id):

                    # Greater than 6 hours
                    if getTimeDifference(instance_id) > 6:

                        # Terminate Instance
                        ec2client.terminate_instances(InstanceIds=[instance_id])
                        # Send Email
                        sendEmail(
                            getEmailAddr(instance),
                            termination_subject.format(instance_id),
                            "",
                        )
                        # Delete DB logs
                        deleteLogs(instance_id)

                else:
                    # Send email
                    sendEmail(
                        instance["Tags"]["created_by"],
                        subject.format(instance_id),
                        message.format(getMissingTags(instance)),
                    )

                    # log time in dynamoDB
                    logEmailTime(instance)

    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
