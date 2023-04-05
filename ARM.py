# !pip install pandas
# !pip install mlxtend
# !pip install numpy
# !pip install ipynb
# !pip install oracledb
# !pip install googletrans==3.1.0a0

import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import numpy as np
import oracledb
from datetime import datetime
import time
from preprocessing_ARM import extractData, formatData, poolData, calcProcessTime
import os

db = ""
with oracledb.connect(db) as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT NO_TRANS FROM AAA_ARM_VAR")
        max_column = cursor.fetchall()
        cursor.execute("SELECT * FROM AAA_ARM_FREQ_SET")
        freq_data = cursor.fetchall()
        cursor.execute("SELECT TAGNAME FROM AAA_ARM_ALARM_DATA")
        alm_data_ori = cursor.fetchall()
max_column = int(list(max_column[0])[0])
freq_data = pd.DataFrame(list(freq_data))
freq_data.columns = ["support", "itemsets"]
alm_data_ori = list(alm_data_ori)
alm_lst = []
for i in alm_data_ori:
    alm_lst.append(str(i).strip("(,)").replace("'",""))

df, alm_data = extractData("new_data.txt")
df, clean_data, uni_tag = formatData(df)
df = poolData(df)
lst = df[1].to_list()
lst = [str(i).strip('][').split(', ') for i in lst]
te = TransactionEncoder()
te_ary = te.fit(lst).transform(lst)
new_df = pd.DataFrame(te_ary)
new_df.columns = uni_tag[0].tolist()
re = fpgrowth(new_df, min_support=0.01, use_colnames=True)

thres = 0.01
t1 = max_column
t2 = int(new_df.shape[0])
for i in freq_data.index:
    f1 = float(freq_data["support"][i])
    check = 0
    for j in re.index:
        if freq_data["itemsets"][i] == str(re["itemsets"][j]):
            check = 1
            f2 = float(re["support"][j])
            freq_data.loc[i, "support"] = ((f1*t1)+(f2*t2))/(t1+t2)
    if check == 0:
        freq_data.loc[i, "support"] = (f1*t1)/(t1+t2)
if (t2/t1) >= thres:       
    for i in re.index:
        f2 = float(re["support"][i])
        sup = (f2*t2)/(t1+t2)
        if sup >= thres:
            freq_data.loc[len(freq_data.index)] = [sup, re["itemsets"][i]]
t1 = t1 + t2
freq_data["itemsets"] = [frozenset(str(i).strip("frozenset").strip("(){}").replace("'", "").replace(" ", "").split(",")) for i in freq_data["itemsets"]]
res = association_rules(freq_data, metric="confidence", min_threshold=0.95)
res["antecedents"] = res["antecedents"].apply(lambda x: ', '.join(list(x))).astype("unicode")
res["consequents"] = res["consequents"].apply(lambda x: ', '.join(list(x))).astype("unicode")
res = res.replace(np.inf, 10000)

alm_data = alm_data.reset_index()
new_alm_lst = []
for i in alm_data["TagName"]:
    vald = 0
    for j in alm_lst:
        if str(i) == str(j):
            vald = 1
    if vald == 0:
        new_alm_lst.append(str(i))
new_alm_df = alm_data[alm_data["TagName"].isin(new_alm_lst)].values.tolist()
clean_data = clean_data.values.tolist()
time_ = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
freq_data = freq_data.values.tolist()
res = res.values.tolist()
t_item = len(new_alm_df) + len(clean_data) + 2 + len(freq_data) + len(res)
c_item = 1

start = time.time()
with oracledb.connect(db) as connection:
    with connection.cursor() as cursor:
        
        calcProcessTime(start, c_item, t_item)
        for x, i in enumerate(new_alm_df):
            cursor.execute("INSERT INTO AAA_ARM_ALARM_DATA VALUES(:1, :2, :3, :4, :5, :6, :7)", [i[0], i[1], i[2], i[3], i[4], i[5], i[6]])
            if x % 100 == 0:
                    cursor.execute('commit')
            c_ = c_item + x + 1
            calcProcessTime(start, c_, t_item)
        cursor.execute('commit')
        c_item = c_item + len(new_alm_df)
        
        for x, i in enumerate(clean_data):
            cursor.execute("INSERT INTO AAA_ARM_ALARM_HIST VALUES(:1, :2)", [i[0], i[1]])
            if x % 100 == 0:
                    cursor.execute('commit')
            c_ = c_item + x + 1
            calcProcessTime(start, c_, t_item)
        cursor.execute('commit')  
        c_item = c_item + len(clean_data)
        
        cursor.execute("UPDATE AAA_ARM_VAR SET NO_TRANS = :1, LAST_MODF_DATE = :2", [str(t1), time_])
        cursor.execute('commit') 
        c_item = c_item + 2
        calcProcessTime(start, c_item, t_item)
        
        cursor.execute("DELETE FROM AAA_ARM_FREQ_SET")
        cursor.execute('commit')
        for x, i in enumerate(freq_data):
            cursor.execute("INSERT INTO AAA_ARM_FREQ_SET VALUES(:1, :2)", [i[0], str(i[1])])
            if x % 100 == 0:
                cursor.execute('commit')
            c_ = c_item + x + 1
            calcProcessTime(start, c_, t_item)
        cursor.execute('commit')   
        c_item = c_item + len(freq_data)
        
        cursor.execute("DELETE FROM AAA_ARM_RULE")
        cursor.execute('commit')
        for x, i in enumerate(res):
            cursor.execute("INSERT INTO AAA_ARM_RULE VALUES(:1, :2, :3, :4, :5, :6, :7, :8, :9)", [i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8]])
            if x % 100 == 0:
                cursor.execute('commit')
            c_ = c_item + x + 1
            calcProcessTime(start, c_, t_item)
        cursor.execute('commit')
        c_item = c_item + len(res)
        calcProcessTime(start, c_item, t_item)

os.remove("new_data.txt")