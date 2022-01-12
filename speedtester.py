from datetime import datetime
from time import sleep

import speedtest
import pandas as pd

NUMBER_OF_TESTS_PER_HOUR = 12
TIMEOUT = 300


def get_internet_info(st):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    return {"download": round(st.download()/10**6, 3),
            "upload": round(st.upload()/10**6, 3),
            "ping": st.results.ping,
            "date": date,
            "time": current_time,
            }


def get_hourly_stats(df, index, internet_info):
    download = df.get("download")
    upload = df.get("upload")

    stats = {"average download(Hour)": download.mean(),
             "minimum download(Hour)": download.min(),
             "maximum download(Hour)": download.max(),
             "average upload(Hour)": upload.mean(),
             "minimum upload(Hour)": upload.min(),
             "maximum upload(Hour)": upload.max()}

    for key in stats:
        print(f"{key}: {stats[key]}")
        df.loc[index, key] = stats[key]


def run(st, df):
    internet_info = get_internet_info(st)
    number_of_tests = 0
    while True:
        print("*"*25 + f"\ndownload: {internet_info.get('download')} Mbps\nupload: {internet_info.get('upload')} Mbps"
                       f"\nping: {internet_info.get('ping')} ms\ndate: {internet_info.get('date')}\n"
                       f"time: {internet_info.get('time')}")

        df = df.append(internet_info, ignore_index=True)
        number_of_tests += 1

        if number_of_tests == NUMBER_OF_TESTS_PER_HOUR:
            index = df.last_valid_index()
            get_hourly_stats(df, index, internet_info)
            number_of_tests = 0
        sleep(TIMEOUT)

        df.to_csv("data.csv", index=False)
        internet_info = get_internet_info(st)


if __name__ == "__main__":
    st = speedtest.Speedtest()
    st.get_best_server()
    df = pd.DataFrame()
    run(st, df)
