import argparse
import glob
from pathlib import Path

import pandas as pd


def merge_got(fp_got):
    """Merge files"""

    if not isinstance(fp_got, list):
        fp_got = [fp_got]

    dfs = [pd.read_csv(f, usecols=['date', 'id']) for f in fp_got]
    print("merging {} files".format(len(dfs)))
    got_statuses = pd.concat(dfs, axis=0)
    got_statuses.drop_duplicates("id", inplace=True)
    print("{} statuses found".format(got_statuses.shape[0]))
    return got_statuses


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Merges getOldTweets scrape runs and do some preprocessing.'
    )
    parser.add_argument('input_fp', type=str, nargs="*", help='source file')
    parser.add_argument('-o', "--output_fp", type=str, help='result file')
    args = parser.parse_args()

    df_result = merge_got(args.input_fp)

    output_fp = Path(args.output_fp)
    output_fp.parent.mkdir(parents=True, exist_ok=True)
    df_result.to_csv(output_fp, index=False)
