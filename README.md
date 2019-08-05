# Collect historical tweets with Airflow

This repository contains an [Airflow](https://airflow.apache.org/) workflow
for the collection of historical tweets based on a search query. The method
combines the package [getOldTweets3](https://github.com/Mottl/GetOldTweets3)
with the [Twitter status lookup API](https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-lookup.html).
Airflow is used to make this into structured data pipelines.

The [Twitter Standard Search API](https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets.html)
searches against a sampling of recent Tweets published in the past 7 days.
Therefore, this API is not very useful to collect historical tweets.
The package getOldTweets3 is a webscraping package for Twitter that was developed to deal bypass this problem. The packages
returns a selection of variables like "id", "permalink", "username", "to",
"text", "date" in UTC, "retweets", "favorites", "mentions", "hashtags" and
"geo". Unfortunately, not all relevant variables are returned and data can be
a bit messy (broken urls). To collect the full set of variables, we can use 
the [Twitter status lookup API](https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-lookup.html).
This API is less restrictive compared to the [Twitter Standard Search API](https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets.html). This project collectes the full set of variables 
after the getOldTweets3 scrape. 

![DAG Twitter](img/dag.png)

## Installation and preparation

This project runs on Python 3.6+ and depends on tools like `Airflow`, `tweepy`
and `getOldTweets3`. Install all the dependencies from the `requirements.txt`
file.

```
pip install -r requirements.txt
```

Create a json file with your twitter credentials (e.g.
`~/Credentials/twitter_cred.json`). Read more about Twitter access tokens on
the [Twitter developer documentation](https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens.html).

```
{
    "consumer_key":"XXXXXXXXXXXXXXXXXXXXXXXXX",
    "consumer_secret":"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "access_token":"00000000-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "access_token_secret":"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
}
```

Initialise and start Airflow. Please read the documentation of Airflow if you
are not familiar with setting up Airflow.

```
export AIRFLOW_HOME=/PATH/TO/YOUR/PROJECT/getOldTweets_airflow

# initialize the database
airflow initdb

# start the web server, default port is 8080
airflow webserver -p 8080

# start the scheduler
airflow scheduler
```

Open another terminal and add the Twitter credentials to the enviroment
variables.

```
export TWITTER_CREDENTIALS=~/Credentials/twitter_cred.json
```

## Usage 

Airflow can be used to schedule jobs, but also do a backfill operation. This
backfill operation is very useful for collecting historical tweets. By
default, pipelines are split into montly intervals.

Edit the search query in the file `dag/dag_tweet_search.py`. Adjust the query
by adjusting `QUERY_SEARCH` and/or `QUERY_LANG`.  It is recommended to save
the file with another file name and `dag_id`.

The following backfill operation collects all tweets from 2018. The results
are stored in 12 different files, one for each month.

```
airflow backfill tweet_collector -s 2018-01-01 -e 2018-12-31
```

Monitor the process with the Airflow GUI. 

![Tree example](img/airflow_tree.png)

The format of this query is: `airflow backfill dag_id -s start_date -e end_date`

Results can be found in the output folder.

## License

[BSD-3](/LICENSE)

## Contact 

This project is a project by [Parisa Zahedi](mailto:p.zahedi@uu.nl) and 
[Jonathan de Bruin](mailto:j.debruin1@uu.nl). 
