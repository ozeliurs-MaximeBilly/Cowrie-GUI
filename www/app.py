import warnings
import time

from tabulate import tabulate
from flask import Flask, render_template, redirect

from tools import *


warnings.filterwarnings("ignore")

app = Flask(__name__)

try:
    dataset = pd.DataFrame()
    for file in Path("./logs").iterdir():
        if file.name == ".DS_Store":
            continue
        l_dataset = read_cowrie_file(str(file))
        dataset = dataset.append(prepare_dataset(l_dataset))
except FileNotFoundError:
    dataset = pd.DataFrame()


@app.route("/")
def home():  # put application's code here

    cc = get_country_counts(dataset)
    dr = get_day_repartition(dataset)

    return render_template("home.html",
                           country_map=get_country_map(dataset),
                           top_ips=get_ip_counts(dataset)[:10],
                           top_country=cc[:10],
                           latest_sessions=get_latest_sessions(dataset)[:10],
                           country_graph=make_pie_chart("Sessions by country", cc["country_short"][:15].tolist(), cc["country_count"][:15].tolist()),
                           top_commands=get_top_commands(dataset)[:15],
                           time_rep=make_bar_chart("Time Repartition", dr["timestamp"].tolist(), dr["day_count"].tolist()))


@app.route("/session/<session_id>")
def session_info(session_id):
    return render_template("session.html",
                           session_info=dataset[dataset["session"] == session_id].sort_values(by="timestamp"))


@app.route("/ip/<ip>")
def ip_info(ip):
    # {"status":"success","country":"Germany","countryCode":"DE","region":"BY","regionName":"Bavaria","city":"Nuremberg","zip":"90475","lat":49.405,"lon":11.1617,"timezone":"Europe/Berlin","isp":"Contabo GmbH","org":"Contabo GmbH","as":"AS51167 Contabo GmbH","query":"167.86.82.168"}

    return render_template("ip_info.html", ip_info=get_ip_info(ip))


@app.route("/refresh")
def refresh():
    global dataset
    l_dataset = read_cowrie_file("./logs/cowrie.json")
    dataset = prepare_dataset(l_dataset)

    return redirect("/")


@app.route("/test")
def test():
    temp = dataset[dataset["eventid"] == "cowrie.command.input"]
    temp = temp["src_ip"].drop_duplicates()
    print(temp)
    for line in temp:
        print(line)
        get_ip_info(line)

    print("done")
    return redirect("/")

@app.route("/health")
def health():
    return "OK"
