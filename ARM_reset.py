import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import numpy as np
import oracledb
from datetime import datetime
import time
from preprocessing_ARM import extractData, formatData, poolData, calcProcessTime
import os

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

t2 = int(new_df.shape[0])
res = association_rules(re, metric="confidence", min_threshold=0.95)
res["antecedents"] = res["antecedents"].apply(lambda x: ', '.join(list(x))).astype("unicode")
res["consequents"] = res["consequents"].apply(lambda x: ', '.join(list(x))).astype("unicode")
res = res.replace(np.inf, 10000)

alm_data = alm_data.reset_index()
new_alm_df = alm_data.values.tolist()
clean_data = clean_data.values.tolist()
time_ = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
freq_data = re.values.tolist()
res = res.values.tolist()
t_item = len(new_alm_df) + len(clean_data) + 2 + len(freq_data) + len(res)
c_item = 1

start = time.time()
db = ""
with oracledb.connect(db) as connection:
    with connection.cursor() as cursor:
        
        calcProcessTime(start, c_item, t_item)
        cursor.execute("DELETE FROM AAA_ARM_ALARM_DATA")
        cursor.execute('commit')
        for x, i in enumerate(new_alm_df):
            cursor.execute("INSERT INTO AAA_ARM_ALARM_DATA VALUES(:1, :2, :3, :4, :5, :6, :7)", [i[0], i[1], i[2], i[3], i[4], i[5], i[6]])
            if x % 100 == 0:
                    cursor.execute('commit')
            c_ = c_item + x + 1
            calcProcessTime(start, c_, t_item)
        cursor.execute('commit')
        c_item = c_item + len(new_alm_df)
        
        cursor.execute("DELETE FROM AAA_ARM_ALARM_HIST")
        cursor.execute('commit')
        for x, i in enumerate(clean_data):
            cursor.execute("INSERT INTO AAA_ARM_ALARM_HIST VALUES(:1, :2)", [i[0], i[1]])
            if x % 100 == 0:
                    cursor.execute('commit')
            c_ = c_item + x + 1
            calcProcessTime(start, c_, t_item)
        cursor.execute('commit')  
        c_item = c_item + len(clean_data)
        
        cursor.execute("DELETE FROM AAA_ARM_VAR")
        cursor.execute('commit')
        cursor.execute("INSERT INTO AAA_ARM_VAR VALUES(:1, :2)", [str(t2), time_])
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

