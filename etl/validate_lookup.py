# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2018, Jonathan de Bruin & Parisa Zahedi
# License BSD3 (See full license)

"""Script to validate the completeness of the lookup process."""

import argparse
import json

import pandas as pd


def validate(got_ids, lookup_ids):
    """Validate results."""
    print(
        "Number of tweets missing in lookup:",
        len(set(got_ids) - set(lookup_ids)),
        "of",
        len(got_ids)
    )


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Validate the completeness of the lookup process.'
    )
    parser.add_argument('got_fp', type=str, help='source dir')
    parser.add_argument("lookup_fp", type=str, help='result dir')
    args = parser.parse_args()

    # got data
    got_ids = pd.read_csv(args.got_fp, usecols=["id"])["id"].tolist()

    # lookup data
    lookup_ids = []
    with open(args.lookup_fp, "r") as f:
        for line in f:
            result = json.loads(line)
            lookup_ids.append(result['id'])

    validate(got_ids, lookup_ids)
