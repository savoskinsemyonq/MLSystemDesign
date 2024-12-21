import requests
import zipfile
import logging

def download_data():
    response = requests.get("https://files.grouplens.org/datasets/movielens/ml-latest-small.zip", verify=False)
    path = "ml-latest-small.zip"
    with open(path, "wb") as file:
        file.write(response.content)
    with zipfile.ZipFile(path, 'r') as zip_file:
        zip_file.extractall("data")
    logging.info("Data downloaded and extracted!!!")