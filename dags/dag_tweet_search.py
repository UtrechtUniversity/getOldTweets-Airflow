# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2018, Jonathan de Bruin & Parisa Zahedi
# License BSD3 (See full license)
#
# Modify the search query. You might have to wait a couple of minutes before
# chnages take place in the Airflow GUI.

"""DAG to collect full information of Twitter search queries."""

import os

from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator

# Twitter config
QUERY_SEARCH = "from:utrechtuni"
LANG_SEARCH = None

# Specific settings for this DAG
NUMBER_OF_GOT_RUNS = 3

# folder settings
DAG_FOLDER = os.path.abspath(os.path.dirname(__file__))
SCRIPTS_FOLDER = os.path.join(DAG_FOLDER, "..", "etl")
OUTPUT_FOLDER = os.path.join(DAG_FOLDER, "..", "output")


args = {
    'owner': 'Utrecht University',
    'depends_on_past': False,
    'start_date': '2007-01-01',
}


dag = DAG(
    dag_id='tweet_collector',
    default_args=args,
    schedule_interval='@monthly',
    params={
        'scripts_folder': SCRIPTS_FOLDER,
        'output_folder': OUTPUT_FOLDER
    }
)

# Operator to validate the results of the getOldTweets runs
validate_get_old_tweets = BashOperator(
    task_id='validate_get_old_tweets',
    bash_command="""
        python {{params.scripts_folder}}/validate_lookup.py \
            {{ params.output_folder}}/get_old_tweets_merged/output_get_old_tweets_{{ ds }}.csv \
            {{ params.output_folder}}/lookup/output_lookup_{{ ds }}.json

    """,
    dag=dag,
)

# Operator for collecting detailed information about the tweets
lookup_tweets = BashOperator(
    task_id='lookup_tweets',
    bash_command="""
        python {{params.scripts_folder}}/lookup.py \
            {{ params.output_folder}}/get_old_tweets_merged/output_get_old_tweets_{{ ds }}.csv \
            {{ params.output_folder}}/lookup/output_lookup_{{ ds }}.json \
            {{ params.output_folder}}/lookup/errors_lookup_{{ ds }}.json

    """,
    dag=dag,
)

# Operator to merge de results from multiple getOldTweets runs
merge_get_old_tweets = BashOperator(
    task_id='merge_get_old_tweets',
    bash_command="""
        python {{params.scripts_folder}}/merge_got.py \
            {{ params.output_folder}}/get_old_tweets_*/output_get_old_tweets_*_{{ ds }}.csv \
            -o {{ params.output_folder}}/get_old_tweets_merged/output_get_old_tweets_{{ ds }}.csv
    """,
    dag=dag,
)

# Operators to collect the data with getOldTweets
for i in range(NUMBER_OF_GOT_RUNS):
    get_old_tweets = BashOperator(
        task_id='get_old_tweets_' + str(i),
        bash_command="""
            mkdir -p {{ params.output_folder}}/{{task.task_id}}
            GetOldTweets3 --querysearch "{{ params.query_search }}" \
                --since "{{ ds }}" --until "{{ next_ds }}" \
                --output "{{ params.output_folder}}/{{task.task_id}}/output_{{task.task_id}}_{{ ds }}.csv"\
                {% if params.lang_search %}--lang params.lang_search{% endif %}
        """,
        dag=dag,
        params={
            'query_search': QUERY_SEARCH,
            'lang_search': LANG_SEARCH
        }
    )
    get_old_tweets >> merge_get_old_tweets

merge_get_old_tweets >> lookup_tweets
lookup_tweets >> validate_get_old_tweets


if __name__ == "__main__":
    dag.cli()
