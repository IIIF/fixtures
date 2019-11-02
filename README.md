





## Architecture

To make responses quicker the filesystem layout is stored in the following file:

 * files.json

This is generated on boot and then updated by subscribing to the SQS topic for the bucket. The SQS messages are generated when there is a change to the underlying s3 bucket. More info:

 * [S3 Notifications](https://docs.aws.amazon.com/AmazonS3/latest/dev/NotificationHowTo.html)
 * [Python client](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-example-sending-receiving-msgs.html)
