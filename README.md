# Fantasy Basketball Lineup Scripts

Within the src/ folder you can find two scripts:

1) setLineup.py - Automatically sets the lineup for teams.
2) benchStarters.py - Benches players in starting lineup if team will be going over the games played limit.

Both scripts use the credentials of league manager and the league manager tool to perform their function on each team in the 'teams' environment variable. 

These scripsts are configured to work on AWS Lambda. I've set triggers to run them at a certain desired time each day.  

At some point down the road I may attempt to clean up the algorithm and make it as efficient as possible.


[Take a look at this blog post](https://robertorocha.info/setting-up-a-selenium-web-scraper-on-aws-lambda-with-python/) for how to set up selenium to run on AWS Lambda.  This was quite painful to figure out, and this helped me get it done.

##### Notes
The way the lineup is set is definitely not the most efficient way, but gets the job done for now. (I'm not 100% sure all corner cases have been handled at the moment) 

### One missing file in the repo!
From the blog post you can see that I am missing one file in my repo: docker-compose.yml  
This is needed to test the lambda locally, amd wasn't included due to my login credentials being there.  Here is how mine looks:
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

### Uploading to AWS lambda:

For me I have a lambda hosting the setLineup script which runs every day, and another lambda hosting the benchStarters script which runs on Fri,Sat,Sun (after the setLineup script is done).

To upload I follow these steps:
1) sudo make build-lambda-package
2) aws cli command to upload zip file to S3 bucket (need to upload to S3 first because size is too large to upload directly to lambda)
3) aws cli command to upload the S3 file to lambda function
