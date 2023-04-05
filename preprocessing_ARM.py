import pandas as pd
import time
import datetime
from datetime import timedelta
from IPython.display import clear_output
from googletrans import Translator


def extractData(file):
    lst = []
    try:
        with open(file, "r", encoding="utf-16") as filestream:
            for line in filestream:
                crline = line.strip("\n").split(",")
                lst.append(crline)
    except:
        with open(file, "r", encoding="utf-8") as filestream:
            for line in filestream:
                crline = line.strip("\n").split(",")
                lst.append(crline)

    df = pd.DataFrame(lst)
    df = df.rename(columns=df.iloc[0]).loc[1:]

    for i, x in enumerate(df['EventStamp']):
        if x == 'EventStamp':
            df = df.drop(labels=i + 1)
            i = i - 1

    df = df.reset_index(drop=True)
    translator = Translator()
    alm_data = df[["TagName", "Description", "Area", "Type", "Priority", "Category", "Provider"]]
    alm_data = alm_data.groupby('TagName').min()
    ItemError_tag = alm_data[alm_data.index.str.endswith('ItemErrorCntAlarm')].index
    ItemError_tag = ItemError_tag.union(alm_data[alm_data.index.str.startswith('test')].index)
    alm_data = alm_data.drop(ItemError_tag, inplace=False)
    alm_data["Description"] = [translator.translate(i).text.replace("电表", "Meter") for i in alm_data["Description"]]
    return df, alm_data


def formatData(df):
    df = pd.DataFrame().assign(EventStamp=df['EventStamp'], TagName=df['TagName'])
    df['EventStamp'] = df['EventStamp'].apply(pd.to_datetime)
    clean_data = df.copy()
    df['TagName'], unique_tag = pd.factorize(df['TagName'])
    uni_tag = pd.DataFrame(unique_tag.to_list())
    return df, clean_data, uni_tag


def calcProcessTime(starttime, cur_iter, max_iter):
    telapsed = time.time() - starttime
    testimated = (telapsed / cur_iter) * (max_iter)
    finishtime = starttime + testimated
    finishtime = datetime.datetime.fromtimestamp(finishtime).strftime("%H:%M:%S")
    lefttime = testimated - telapsed
    prstime = int(telapsed), int(lefttime), finishtime
    print(cur_iter, "out of", max_iter, "|", round((cur_iter / max_iter) * 100, 2), "% completed!")
    print("time elapsed: %s(s), time left: %s(s), estimated finish time: %s" % prstime)
    clear_output(wait=True)


def poolData(df):
    lst = []
    start = time.time()
    interval = 5
    for i in df.index:
        tm_intv = 10

        if (i - tm_intv) <= 0:
            start_intv = 0
        else:
            start_intv = (i - tm_intv)
        while (df['EventStamp'][i] + timedelta(minutes=interval)) < df['EventStamp'][start_intv]:
            start_intv = start_intv - tm_intv
            if start_intv < 0:
                start_intv = 0
                break

        if (i + tm_intv) >= len(df):
            end_intv = len(df) - 1
        else:
            end_intv = (i + tm_intv)
        while (df['EventStamp'][i] + timedelta(minutes=interval)) > df['EventStamp'][end_intv]:
            end_intv = end_intv + tm_intv
            if end_intv > len(df) - 1:
                end_intv = len(df) - 1
                break

        temp_lst = []
        for j in range(start_intv, end_intv + 1):
            if (df['EventStamp'][j] <= (df['EventStamp'][i] + timedelta(minutes=interval))) and (
                    df['EventStamp'][j] >= (df['EventStamp'][i] - timedelta(minutes=interval))):
                temp_lst.append(df['TagName'][j])
        lst.append([df['EventStamp'][i], temp_lst])
        calcProcessTime(start, i + 1, len(df.index))
    pool_data = pd.DataFrame(lst)
    pool_data = pool_data.drop(columns=[0])
    return pool_data
