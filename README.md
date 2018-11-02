# Fantasy Basketball Lineup Setter

A python script to automatically set fantasy basketball lineup on ESPN.  
Uses the credentials of league manager and the league manager tool to set specified team's lineup for that day.  

Script is hosted on an AWS Lambda, and is triggered at a set time each day.

The way the lineup is set is definitely not the most efficient way, but gets the job done for now. (Although there may still be some corner cases)  

At some point down the road I may attempt to clean up the algorithm and make it as efficient as possible.


[Take a look at this blog post](https://robertorocha.info/setting-up-a-selenium-web-scraper-on-aws-lambda-with-python/) for how to set up selenium to run on AWS Lambda.  This was quite painful to figure out, and this helped me get it done.

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
      - teams=Team One,Team Two,Team Three,etc...
      - hasGamesPlayedLimit=True
    volumes:
      - ./src/:/var/task/src/
```

