import logging

import pandas as pd
from pathlib import Path

def split_data():
    data_path = Path("data/ml-latest-small/ratings.csv")
    train_path = Path("data/train.csv")
    test_path = Path("data/test.csv")

    ratings = pd.read_csv(data_path)
    ratings = ratings.sort_values('timestamp')
    indx = int(len(ratings) * 0.8)

    train = ratings.iloc[:indx]
    test = ratings.iloc[indx:]

    train.to_csv(train_path, index=False)
    test.to_csv(test_path, index=False)

    logging.info(f"Train size: ({len(train)}) Test size: ({len(test)}).")