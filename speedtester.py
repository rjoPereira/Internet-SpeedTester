import time
from datetime import datetime

import speedtest
import pandas as pd

NUMBER_OF_TESTS_PER_HOUR = 12
TIMEOUT = 300


def get_internet_info(st):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    return {"download": round(st.download() / 10 ** 6, 3),
            "upload": round(st.upload() / 10 ** 6, 3),
            "ping": st.results.ping,
            "date": date,
            "time": current_time,
            }


def get_hourly_stats(df, index):
    last_records = df.tail(NUMBER_OF_TESTS_PER_HOUR)
    download = last_records.get("download")
    upload = last_records.get("upload")

    stats = {"average download(Hour)": download.mean(),
             "minimum download(Hour)": download.min(),
             "maximum download(Hour)": download.max(),
             "average upload(Hour)": upload.mean(),
             "minimum upload(Hour)": upload.min(),
             "maximum upload(Hour)": upload.max()}

    for key in stats:
        print(f"{key}: {stats[key]} Mbps")
        df.loc[index, key] = stats[key]


def run(st, df):
    number_of_tests = 0
    while True:
        start = time.time()
        internet_info = get_internet_info(st)
        print("*" * 25 + f"\ndownload: {internet_info.get('download')} Mbps\nupload: {internet_info.get('upload')} Mbps"
                         f"\nping: {internet_info.get('ping')} ms\ndate: {internet_info.get('date')}\n"
                         f"time: {internet_info.get('time')}")

        df = df.append(internet_info, ignore_index=True)
        number_of_tests += 1
        time_elapsed = time.time() - start

        if number_of_tests == NUMBER_OF_TESTS_PER_HOUR:
            index = df.last_valid_index()
            get_hourly_stats(df, index)
            number_of_tests = 0

        df.to_csv("data.csv", index=False)
        time.sleep((TIMEOUT - time_elapsed) if time_elapsed < TIMEOUT else 0)


if __name__ == "__main__":
    try:
        df = pd.read_csv("data.csv")
    except FileNotFoundError:
        df = pd.DataFrame()
        df.append(["download", "upload", "ping", "date", "time"])

    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        run(st, df)
    except speedtest.ConfigRetrievalError:
        print("Couldn't connect to a server.")

