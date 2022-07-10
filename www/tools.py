import random
import string
from io import StringIO
from pathlib import Path

import IP2Location
import folium
import requests

import pandas as pd
import seaborn as sns
import multiprocessing as mp
import numpy as np

from tqdm import tqdm
from tabulate import tabulate

database = IP2Location.IP2Location(Path(__file__).parent / "data/IP2LOCATION-LITE-DB11.IPV6.BIN")


def get_ip_info(ip):
    return requests.get(f"https://api.ozeliurs.com/ip/{ip}").json()


def read_cowrie_file(filename: str):
    print(f"Reading {filename}")
    log_file = Path(filename).read_text()
    json_logs = StringIO("[" + ",\n".join(log_file.split("\n")[:-1]) + "]")
    return pd.read_json(json_logs)


def load_all(threads: int = 6):
    files = [x for x in Path("./logs").iterdir() if x.name != ".DS_Store"]
    return pd.concat(mp.Pool(threads).map(thread_job, np.array_split(files, threads)), ignore_index=True)


def thread_job(file_list):
    local_df = pd.DataFrame()
    for file in file_list:
        local_df = local_df.append(read_cowrie_file(str(file)))
    return prepare_dataset(local_df)


def ip_complete(input_df: pd.Series) -> pd.Series:
    if input_df["eventid"] != "cowrie.session.connect":
        return input_df

    ip_info = database.get_all(input_df["src_ip"])

    input_df["country_short"] = ip_info.country_short
    input_df["isp"] = ip_info.isp

    return input_df


def prepare_dataset(input_df: pd.DataFrame) -> pd.DataFrame:
    input_df = input_df.apply(ip_complete, axis=1)

    return input_df


def get_country_map(df):
    df = get_country_counts(df)

    m = folium.Map()

    folium.Choropleth(
        geo_data="./data/custom.geo.json",
        name='choropleth',
        data=df,
        columns=['country_short', "country_count"],
        key_on='feature.properties.iso_a2',
        fill_color='PuBuGn',
        fill_opacity=0.9,
        line_opacity=0.2,
        legend_name='IP of Origin',
    ).add_to(m)

    return m._repr_html_()


def get_country_counts(df):
    df = df[df["eventid"] == "cowrie.session.connect"]
    df = df.value_counts(["country_short"]).reset_index(name='country_count')

    return df.sort_values(by=['country_count'], ascending=False)


def get_ip_counts(df):
    df = df[df["eventid"] == "cowrie.session.connect"]
    df = df.value_counts(["src_ip"]).reset_index(name='ip_count')

    return df.sort_values(by=['ip_count'], ascending=False)


def get_latest_sessions(df):
    df = df[df["eventid"] == "cowrie.session.connect"]

    return df.sort_values(by=["timestamp"], ascending=False)


def get_top_commands(df):
    df = df[df["eventid"] == "cowrie.command.input"]

    df = df.value_counts(["input"]).reset_index(name="input_count")

    df = df[["input", "input_count"]].drop_duplicates()

    return df


def make_pie_chart(title: str, labels: list, data: list):
    chart_id = "".join(random.choice(string.ascii_letters) for _ in range(10))
    labels = [str(x) for x in labels]
    data = [str(x) for x in data]
    palette = sns.color_palette("mako", len(labels))[::-1]

    html = """
        <canvas id=" """ + chart_id + """ " width="400" height="400"></canvas>
        <script>
        const """ + chart_id + """ctx = document.getElementById(' """ + chart_id + """ ').getContext('2d');
        const """ + chart_id + """Chart = new Chart(""" + chart_id + """ctx, {
            type: 'pie',
            data: {
                labels: [""" + ",".join([f"'{x}'" for x in labels]) + """],
                datasets: [{
                    label: '""" + title + """',
                    data: [""" + ",".join(data) + """],
                    backgroundColor: [""" + ",".join([f"'rgb({round(x[0]*255)}, {round(x[1]*255)}, {round(x[2]*255)})'" for x in palette]) + """],
                hoverOffset: 4
                }]
            }
        });
        </script>
    """

    return html


def get_day_repartition(df):
    df = df[df["eventid"] == "cowrie.session.connect"]

    df["timestamp"] = df["timestamp"].apply(lambda x: x.date)

    df = df.value_counts(["timestamp"]).reset_index(name='day_count')

    return df.sort_values(by="timestamp", ascending=False)


def get_top_asn(df):
    # Not enough info

    df = df[df["eventid"] == "cowrie.session.connect"]

    return []


def make_bar_chart(title: str, labels: list, data: list):
    chart_id = "".join(random.choice(string.ascii_letters) for _ in range(10))
    labels = [str(x) for x in labels]
    data = [str(x) for x in data]
    palette = sns.color_palette(None, 1)

    html = """
        <canvas id=" """ + chart_id + """ " width="400" height="400"></canvas>
        <script>
        const """ + chart_id + """ctx = document.getElementById(' """ + chart_id + """ ').getContext('2d');
        const """ + chart_id + """Chart = new Chart(""" + chart_id + """ctx, {
            type: 'bar',
            data: {
                labels: [""" + ",".join([f"'{x}'" for x in labels]) + """],
                datasets: [{
                    label: '""" + title + """',
                    data: [""" + ",".join(data) + """],
                    backgroundColor: [""" + ",".join([f"'rgb({round(x[0]*255)}, {round(x[1]*255)}, {round(x[2]*255)})'" for x in palette]) + """],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        </script>
    """

    return html

