# Fantasy Basketball Lineup Scripts

Within the src/ folder you can find two scripts:

1) **setLineup.py** - Automatically sets the lineup for teams.
2) **benchStarters.py** - Benches players in starting lineup if team will be going over the games played limit.

Both scripts use the credentials of league manager and the league manager tool to perform their function on each team in the 'teams' environment variable. 

These scripts are configured to work on AWS Lambda. I've set triggers to run them at a certain desired time each day.  

##### Notes
The way the lineup is set is definitely not the most efficient way, but gets the job done for now. (I'm not 100% sure all corner cases have been handled at the moment). At some point down the road I may attempt to clean up the algorithm and make it cleaner/more efficient.

Currently in my leagues with 12 teams, both scripts take around 3-5 minutes each to complete all teams.  On AWS Lambda I've allocated 2048 mb of memory for the functions.

### One missing file in the repo!
From the blog post (see below) you can see that I am missing one file in my repo: docker-compose.yml  
This is needed to test the lambda locally, and wasn't included due to my login credentials being there.  Here is how mine looks:
```
version: '3'

services:
  lambda:
    build: .
    environment:
      - PYTHONPATH=/var/task/src:/var/task/lib
      - PATH=/var/task/bin
      - email=INSERT EMAIL HERE
      - leagueId=INSERT LEAGUE ID HERE
      - password=INSERT PASSWORD HERE
      - teams=Team One,Team Two,Team Three,etc...(script assumes team names separated by a comma and no space)
    volumes:
      - ./src/:/var/task/src/
```

### Setting things up
[Take a look at this blog post](https://robertorocha.info/setting-up-a-selenium-web-scraper-on-aws-lambda-with-python/) and follow the steps to get your workspace setup to deploy a python selenium script to run on AWS Lambda.  This was quite painful to figure out, and the blog post helped me immensely. 

Make sure you install Docker AND Docker Compose.  And you can install the dependencies by running ```sudo make fetch-dependencies```.

### Testing locally
1) sudo make docker-build
2) sudo make docker-run-setlineup OR sudo make docker-run-benchstarters

### Uploading to AWS lambda:

For me I have a lambda hosting the setLineup script which runs every day, and another lambda hosting the benchStarters script which runs on Fri,Sat,Sun (after the setLineup script is done).

To upload I follow these steps:
1) sudo make build-lambda-package
2) aws cli command to upload zip file to S3 bucket (need to upload to S3 first because size is too large to upload directly to lambda)
   - If creating for the first time: ```aws s3 mb s3://BUCKET_NAME``` (creates your bucket)
   - Upload the zipfile to the bucket: ```aws s3 cp build.zip s3://BUCKET_NAME```
3) aws cli command to upload the S3 file to lambda function
   - If creating for the first time: ```aws lambda create-function --region us-east-2 --function-name YOUR_FUNCTION_NAME --handler (benchStarters.lambda_handler OR setLineup.lambda_handler) --runtime python3.6 --timeout 900 --memory-size 2048 --role [THE ARN OF YOUR IAM ROLE WHICH CAN DEPLOY TO LAMBDA] --code S3Bucket=BUCKET_NAME,S3Key=build.zip```
   - If updating your existing lambda: ```aws lambda update-function-code --function-name YOUR_FUNCTION_NAME --s3-bucket BUCKET_NAME --s3-key build.zip```


Once you upload to Lambda, make sure you include the correct environment variables (the ones in the docker-compose.yml that I did not include).