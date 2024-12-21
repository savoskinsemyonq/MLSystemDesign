import os
import sys
sys.path.append('.')

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, FloatType, IntegerType
from pyspark.ml.recommendation import ALS
from dotenv import load_dotenv
import logging

load_dotenv()


minio_access_key = os.getenv("MINIO_ACCESS_KEY")
minio_secret_key = os.getenv("MINIO_SECRET_KEY")
minio_backet = os.getenv("BUCKET_NAME")
minio_endpoint = "http://minio-server:9000"

logging.info("Create Spark session.")
spark = SparkSession.builder \
    .appName(minio_backet) \
    .master("spark://spark-master:7077") \
    .getOrCreate()

spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.access.key", 
                                                os.getenv("AWS_ACCESS_KEY_ID", minio_access_key))
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.secret.key", 
                                                os.getenv("AWS_SECRET_ACCESS_KEY", minio_secret_key))
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.endpoint",
                                                os.getenv("ENDPOINT", minio_endpoint))
spark.conf.set("fs.s3a.proxy.host", "minio-server")
spark.conf.set("fs.s3a.proxy.port", 9000)
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "true")
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.attempts.maximum", "1")
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.connection.establish.timeout", "5000")
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.connection.timeout", "10000")
spark.sparkContext.setLogLevel("WARN")

logging.info("Spark session created successfully.")

schema = StructType([
    StructField("userId", IntegerType(), True),
    StructField("movieId", IntegerType(), True),
    StructField("rating", FloatType(), True),
    StructField("timestamp", IntegerType(), True)
])

logging.info("Loading train and test datasets from minio.")
train_path = f"s3a://{minio_backet}/train.csv"
test_path = f"s3a://{minio_backet}/test.csv"

try:
    train_data = spark.read.csv(train_path, header=True, schema=schema)
    test_data = spark.read.csv(test_path, header=True, schema=schema)
except Exception as e:
    logging.error(f"Failed to read datasets: {e}")
    spark.stop()

logging.info("Previewing train and test datasets.")
train_data.show(20, False)
test_data.show(20, False)

logging.info("Training ALS model.")
als = ALS(userCol="userId", itemCol="movieId", ratingCol="rating", coldStartStrategy="drop")
try:
    model = als.fit(train_data)
    logging.info("Model trained")
except Exception as e:
    logging.error(f"Model training failed: {e}")
    spark.stop()

logging.info("Start saving the trained model.")
try:
    model.save(f"s3a://{minio_backet}/model")
    logging.info("Model saved!")
except Exception as e:
    logging.error(f"Failed to save the model: {e}")

logging.info("Start making predictions")
try:
    predictions = model.transform(test_data)
    predictions.write.format("csv").mode("overwrite").save(f"s3a://{minio_backet}/predictions")
    logging.info("Predictions are saved.")
except Exception as e:
    logging.error(f"Error in predictions: {e}")

spark.stop()
