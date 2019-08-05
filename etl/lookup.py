import argparse
import json
import os
from pathlib import Path

import tweepy
import pandas as pd


def lookup_tweets(api, ids, chunk_size=100):
    """Lookup a list of statuses."""

    status_results = []
    status_errors = []

    chunks = [ids[x:x+chunk_size] for x in range(0, len(ids), chunk_size)]

    for i, chunk in enumerate(chunks):

        print("Query chunk {}:{} of {}".format(
            i*chunk_size+1, min((i+1)*chunk_size, len(ids)), len(ids)))

        try:
            # start collection tweets
            api_tweets_response = api.statuses_lookup(
                chunk,
                include_entities=True,
                tweet_mode='extended'
            )

            # store the _json of all results
            for status in api_tweets_response:
                status_results.append(status._json)

        except tweepy.TweepError as err:
            print(err.api_code, err.response.reason)

            # safe status errors
            for status_id in chunk:
                status_errors.append({
                    "id": chunk,
                    "code": err.api_code,
                    "message": err.response.reason
                })

    return status_results, status_errors


def lookup_getoldtweets_file(api, input_fp, results_fp, error_fp=None):
    """Perform a lookup for getOldTweets file."""

    # open file
    tweets = pd.read_csv(input_fp, usecols=["id"])
    status_ids = tweets['id'].tolist()

    print(len(status_ids), "tweets found")

    # lookup tweets
    status_results, status_errors = lookup_tweets(api, status_ids)

    # write succesfull retrievals to file
    results_fp = Path(results_fp)
    results_fp.parent.mkdir(parents=True, exist_ok=True)
    with open(results_fp, "w") as f:
        for status in status_results:
            f.write(json.dumps(status) + "\n")

    # write unsuccesfull retrievals to file
    if error_fp and len(status_errors) > 0:
        error_fp = Path(error_fp)
        error_fp.parent.mkdir(parents=True, exist_ok=True)
        with open(error_fp, "w") as f:
            for status_err in status_errors:
                f.write(json.dumps(status_err) + "\n")

    print("{} tweets found, {} errors".format(
        len(status_results), len(status_errors))
    )


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Process getOldTweets file.'
    )
    parser.add_argument('input_fp', type=str, help='source file')
    parser.add_argument('results_fp', type=str, help='results file')
    parser.add_argument('error_fp', type=str, help='error file')
    parser.add_argument('--twitter_cred', type=str, default=None, help='error file')
    args = parser.parse_args()

    # setup twitter authentication
    try:
        twitter_cred_fp = args.tweet_cred
    except AttributeError:
        twitter_cred_fp = os.environ['TWITTER_CREDENTIALS']

    with open(twitter_cred_fp) as f:
        twitter_cred = json.load(f)

    auth = tweepy.OAuthHandler(
        twitter_cred['consumer_key'], twitter_cred['consumer_secret']
    )
    auth.set_access_token(
        twitter_cred['access_token'], twitter_cred['access_token_secret']
    )

    api = tweepy.API(
        auth,
        retry_count=3,
        retry_delay=2,
        wait_on_rate_limit=True,  # wait on rate limit
        wait_on_rate_limit_notify=True
    )

    lookup_getoldtweets_file(
        api,
        args.input_fp,
        args.results_fp,
        args.error_fp
    )
