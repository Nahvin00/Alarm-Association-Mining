# Alarm-Association-Mining
## Problem statement

The Wonderware Historian (recently rebranded as AVEVA Historian) is a real-time relational database for plant data. The historian acquires and stores process data at full resolution and provides real-time and historical plant data together with configuration, event, summary, and associated production data to client applications on the desktop. The historian combines the power and flexibility of Microsoft SQL Server with the high-speed acquisition and efficient data compression characteristics of a real-time system.

IFMY IT FSC MFW team uses Wonderware Historian to manage alarms from sensors at the plant. Although Wonderware can show visualizations and alert of alarms to staff, it still cannot provide insights or patterns of correlation among the alarms. 

## Task specification
A solution for alarm association mining was assigned to develop that:

* Implements AI concepts to obtain alarm pattern
* Retrieves and updates alarm data and patterns continuously, and
* Shows visualization of alarm data and it pattern with interactive dashboard

## Implementation and solution method
This is one of the major projects that took around five (5) months to be completed. As the first step, discussions were carried out to discuss the possible implementation of AI into the alarm management system. After several discussions, it was decided on implementing ARM to alarm data which will give valuable insights about the alarm patterns. Some slides were prepared and the idea was proposed to the manager which he approved. The proposed Alarm Association Mining has a general architecture as shown in figure below.

<p align="center" width="100%">
    <img width="80%" src="https://user-images.githubusercontent.com/55419300/230061095-c5000c15-6b7e-466a-ac21-d5d082f9200c.png">
</p>

After approval, the pipeline of the project was outlined to ensure consistent development and progress. 

### Data extraction
The development of the project began with data extraction. WUXI has been selected as a training site due to its small size. Alarm data of this WUXI site is stored in Microsoft SQL Server which can be accessed by using Microsoft SQL Server Management Studio. Unfortunately, Microsoft SQL Server Management Studio does not have a feature to download data in bulk. This was resolved with Microsoft Visual Studio SSIS tools which can export large amounts of data by configuring control and data flow. After several days of experimentation, a way to use SSIS tools to export alarm data with a duration of little more than one (1) month as a '.txt' file was finally figured out. Text files were used due to large data size and unlike other formats text files do not have a size (or row) limit. Since, extracting bulk data at once would stress the database and might lead to database collapse, it was recommended by colleagues to retrieve data in an interval of 1 week. Hence, a for loop was introduced to iterate data retrieval for each week until the present date and time. Upon executing the SSIS control flow, a text file called ‘new_data.txt’ will be generated with alarm data.

### Data preprocessing
After the data had been extracted, it was time to preprocess the data. Python programming language was used to process and store the data with JupyterLab. This is because Jupyter is more suitable as a prototyping tool for prototyping models and doing a quick analysis of data. The generated text file was read and stored as a pandas dataframe. A simple EDA was conducted on the data to analyze and investigate data sets and summarize their main characteristics. In the dataset there were a total of 22 columns with unique functions. This project focuses only on alarms with ‘UNACK_ALM’ as ‘AlarmState’ which is the first-time alarm that is triggered. The remaining data were filtered out.


This dataframe was then used to produce a copy which only includes columns that are necessary for ARM which are ‘TagName’ and ‘EventStamp’. ‘EventStamp’ is a string field that contains datetime value which was reformatted to datetime format. This dataframe was then used to performed visualization which generated a line graph of ‘TagName’ count across days as in figure below.

<p align="center" width="100%">
    <img width="80%" src="https://user-images.githubusercontent.com/55419300/230058231-8288c9ee-d416-44c0-9c97-8e601fdc7a95.png">
</p>

Patterns in the figure above show a lot of irregularities such as a long line in the middle and a group of alarms occurring together. Alarms are supposed to be random with no visible patterns. Upon inspection, it was found that the most frequently occurring alarms contained 'ItemErrorCntAlarm' as their suffix, which is one of the system-generated alarms triggered when the system loses connection with plant sensors. Figure below shows the trendline of alarms with ‘ItemErrorCntAlarm’ as their suffix.

<p align="center" width="100%">
    <img width="80%" src="https://user-images.githubusercontent.com/55419300/230058257-ae6a39e4-8f36-499c-a6ae-5dd9c37337b1.png">
</p>

If these alarm data are included in the ARM it would create unnecessary pattern association with these alarms that are irrelevant. Another visualization of the trendline of alarms were done by excluding the alarms with ‘ItemErrorCntAlarm’ as their suffix which produced a graph as in figure below.

<p align="center" width="100%">
    <img width="80%" src="https://user-images.githubusercontent.com/55419300/230058284-91a932f5-d947-4a8d-978b-6a0426711e16.png">
</p>

The figure above shows a trendline that is very random like how alarm data should look like. Based on the EDA, all the alarms with ‘ItemErrorCntAlarm’ as their suffix were removed from the original dataframe. From the modified dataframe, two (2) subset dataframe was created: one that stores unique alarm data and another to store the data for ARM. 

### Data preparation
Once the data is preprocessed dataframe containing data for ARM is prepared by factorizing. Factorizing is a process of tagging column using unique number. ‘TagName’ contains long string ID which can make the process slow hence, it is very necessary to convert these string ID to short numeric ID. ARM requires a basket (pool) data to generate association rules. In order to create pool data, a new algorithm was developed to pool alarm data together if it were to trigger within an interval of +/- 5 minutes. To narrow the scope, it was assumed that any two alarms that trigger after more than 10 minutes of the other are considered unrelated. 5 minutes has been decided as the threshold because range of [-5, +5] creates a span of 10 minutes which is significant for the patterns to occur. Once the pool data has been created, it is then encoded to fix the length of data. Encoding is the process of putting a sequence of characters (letters, numbers, punctuation, and certain symbols) into a specialized format for efficient transmission or storage. 

### Association rule mining
ARM can be performed using a frequent itemset which comprises the set of items and its support. Support in this context means ratio of itemset records over total records. These frequent itemset can be generated using two (2) popular algorithms which are Apriori and FP-Growth. Apriori algorithm proceeds by identifying the frequent individual items in the database and extending them to larger and larger item sets as long as those item sets appear sufficiently often in the database. FP-Growth Algorithm is an alternative way to find frequent item sets without using candidate generations, thus improving performance. Both of these algorithms were evaluated with several experiments using a transaction dataset with 56765 records and results are as shown in the table below. Results from the experimentation have also been plotted in a line graph as in figure below.

<p align="center" width="100%">
    <img width="100%" src="https://user-images.githubusercontent.com/55419300/230056914-35ff945a-75ef-49a3-acb0-6b960ffe4e62.png">
</p>
<p align="center" width="100%">
    <img width="80%" src="https://user-images.githubusercontent.com/55419300/230057241-767113a3-c759-4295-8d83-c9df0100dacf.png">
</p>

Based on the graph above, it can be seen that the Apriori algorithm tends to perform faster when the minimum support threshold is higher and vice versa. This is because Apriori needs a generation of candidate itemsets. These itemsets may be large in number if the itemset in the dataset is huge. Apriori also needs multiple scans of the dataset to check the support of each itemset generated and this leads to high costs. Unlike Apriori, FP-Growth seems to be somewhat consistent across different minimum support threshold values. This is because FP-Growth generates frequent itemset without the need for candidate generation.

Due to the reasons mentioned, FP-Growth was selected as the frequent itemset algorithm for this project. 0.01 has been selected as the minimum support which represents 1% from the dataset. Frequent itemset of the pool data was generated using FP-Growth of ‘mlxtend’ python package.

For minimum confidence, the value of 0.95 was used to filter only the most accurate rules. This frequent itemset is then passed on to generate association rules using ‘mlxtend’ python package.

### Visualization
Visualization is a big part of the project which will convey the results to technicians with less technical knowledge. Hence, the dashboard must be simple but comprehensive. Since Infineon Technologies has a license to Tableau, it was used to create the dashboards for this project. To make the visualizations to be continuously updated with new data and patterns, all relevant data required for visualization and processing was uploaded to the oracle database. The table ‘AAA_ARM_ALARM_DATA’ stores the unique alarm data whereas table ‘AAA_ARM_ALARM_HIST’ stores the data for ARM. Table ‘AAA_ARM_FREQ_SET’ stores the generated frequent itemset, ‘AAA_ARM_RULE’ stores the generated association rules and ‘AAA_ARM_VAR’ stores standard variables for processing and also visualizations. Once all the relevant data has been imported to the oracle database, worksheets and dashboards were designed to display processed information.
 
## Results of task/project
At the end of the project, an SSIS project along with three (3) python programs were produced namely ‘preprocessing_ARM.py’, ‘ARM.py’ and ‘ARM_reset.py’. The SSIS project is responsible for retrieving alarm data from Microsoft SQL server and saving it as a text file. ‘preprocessing_ARM.py’ contains functions to preprocess the retrieved alarm data. ‘ARM.py’ can utilize ‘preprocessing_ARM.py’ and its function to process and generate patterns. These generated data will then be stored in the oracle database. ‘ARM_reset.py’ is very similar to ‘ARM.py’ but instead of updating the existing table, this will replace existing data with new data. ‘ARM_reset.py’ functions as a flush for the project to remove irrelevant patterns from the database. All these processed data were stored in the oracle database. 

All these stored data can be visualized using Tableau dashboard. Three (3) dashboards were designed namely ‘Alarm Data’, ‘Top 10 Alarms_’ and ‘Association Rules_’. ‘Alarm Data’ dashboard shows the alarm details including trendlines. It is also equipped with a search bar to search alarms using tag names. Figure below shows the ‘Alarm Data’ dashboard in Tableau. This dashboard is also equipped with a button to navigate to ‘Top 10 Alarms_’ dashboard.

<p align="center" width="100%">
    <img width="80%" src="https://user-images.githubusercontent.com/55419300/230059084-c1e20cb4-7782-438c-9173-c46bf584e5d3.png">
</p>

‘Top 10 Alarms_’ dashboard shows the alarm association for top 10 most occurring frequent itemset. It is also equipped with a confidence filter to limit the number associations shown. Figure below shows the ‘Top 10 Alarms_’ dashboard in Tableau. This dashboard is also equipped with buttons to navigate to ‘Alarm Data’ and ‘Association Rules_’ dashboards.
 
<p align="center" width="100%">
    <img width="80%" src="https://user-images.githubusercontent.com/55419300/230059117-a5a6b43a-70fd-41d0-b7ce-9c911b3bd544.png">
</p>

‘Association Rules_’ dashboard visualizes all association rules in the oracle database. It is also equipped with metric filters such as confidence and support to limit the number associations shown. This dashboard is a complex version of ‘Top 10 Alarms_’ dashboard. Figure below shows the ‘Association Rules_’ dashboard in Tableau. This dashboard is also equipped with a button to navigate to ‘Top 10 Alarms_’ dashboard.

<p align="center" width="100%">
    <img width="80%" src="https://user-images.githubusercontent.com/55419300/230059133-6d7fb73d-c8ad-4ffc-8bac-22df3b5b2632.png">
</p>

Results from this project can be used to alarm patterns that cannot seen with naked eyes. It processes tons and tons of data and shows the most insightful ones. Together with the dashboard, alarm data is now at finger tips with its association and correlations. This project also creates an ecosystem that will continuously update the data and patterns which makes the results continue to evolve with time. It makes it so much easier for data analysts and technicians to figure out the root cause for alarm triggering. ARM rarely gets implemented in industries apart from retail but this project shows that an alarm management system is also a great candidate for ARM implementations.

## Advantage, disadvantage and suggestion for task improvement
In terms of advantage, this solution makes it easier for technicians to fix the machines by identifying the root cause of the alarm. It also allows them to identify defective sensors by its alarm frequency. The dashboard of this project can be used by a person with or without IT/AI knowledge. ‘Top 10 Alarms_’ dashboard is a low-level dashboard that is straight to the point why only showing top 10 alarms that frequently trigger whereas ‘Association Rules_’ dashboard is more of a complex version that visualizes all the generated rules and provides an option to filter by metric. This can also be used by data analysts to evaluate machines and their performance. This in return will reduce machines with higher faulty rates thus saving more money to the company.

In terms of disadvantage, this project has a very steep learning curve so it will take quite some time to completely understand how it works. Apart from that, the project is currently hosted in a local desktop and it might be troublesome to execute the codes frequently. 

In terms of suggestions, the solution can be hosted on a server which will run the code upon scheduling it and it does not have any downtime. Other than that, the project can further develop to incorporate an alarm prediction model. The similar data from the pooling algorithm or sequence data can be used to predict upcoming alarms. 
