from datetime import datetime

# Send email
def sendEmail(recipient, subject, message):

    from lambda_function import ses

    response = ses.send_email(
        Source=recipient,
        Destination={
            "ToAddresses": [
                recipient,
            ],
        },
        Message={"Subject": {"Data": subject}, "Body": {"Text": {"Data": message}}},
    )


# Checks whether the instance contains the empty tags
def checkEmptyTags(instance):

    missingTags = []

    from lambda_function import tagstoCheck

    for tag in instance["Tags"]:
        if tag["Key"] in tagstoCheck and tag["Value"] == "":
            missingTags.append(tag["Key"])

    if len(missingTags) > 0:
        return True

    return False


# Returns list of missing tags
def getMissingTags(instance):

    missingTags = []

    from lambda_function import tagstoCheck

    for tag in instance["Tags"]:
        if tag["Key"] in tagstoCheck and tag["Value"] == "":
            missingTags.append(tag["Key"])

    return missingTags


# Creates missing tags if not present
def createTagsifEmpty(instance):
    tags = {}

    from lambda_function import tagstoCheck, ec2

    for tag in instance["Tags"]:
        tags[tag["Key"]] = tag["Value"]

    for tag in tagstoCheck:

        if tag not in tags:

            ec2.create_tags(
                Resources=instance["InstanceId"], Tags=[{"Key": tag, "Value": ""}]
            )


# Gets email address using the created_by tag
def getEmailAddr(instance):

    for tag in instance["Tags"]:
        if tag["Key"] == "created_by":
            return tag["Value"]


# Check if email was sent already
def checkEmailSent(instance_id):

    from lambda_function import table, dynamodb

    if dynamodb.get_item(TableName=table, Key={"instanceId": {"S": instance_id}}):
        return True

    return False


def getTimeDifference(instance_id):

    from lambda_function import table, dynamodb

    timefromDB = dynamodb.get_item(
        TableName=table, Key={"instanceId": {"S": instance_id}}
    )['Item']['email_time']

    emailTime = datetime.fromisoformat(timefromDB)

    currentTime = datetime.utcnow()

    duration = currentTime - emailTime
    duration_in_s = duration.total_seconds()  # Total number of seconds between dates

    hours = divmod(duration_in_s, 3600)[0]

    return hours


def logEmailTime(instance_id):

    from lambda_function import table, dynamodb

    item = {
        "instanceId": {
            "S": instance_id,
        },
        "email_time": {"S": datetime.utcnow().isoformat()},
    }

    dynamodb.put_item(TableName=table, Item=item)


def deleteLogs(instance_id):

    from lambda_function import table, dynamodb

    item = {
        "instanceId": {
            "S": instance_id,
        }
    }

    dynamodb.delete_item(TableName=table, Item=item)
