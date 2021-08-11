# Data Quality Engineer Challenge

Welcome to the HAMS Data Quality Engineer Challenge! With this challenge we want to test your ability to analyze the data in the accompanying database and find potential data quality issues.


## Task
Obviously, we want you to analyze the data in the database file **[challenge.db](challenge.zip)** file. This is a Zipped SQLite database with the following [schema](challenge_db_create.sql).

The data belongs to a company called **Company X** and contains information of e-commerce purchases that were made with Company X. Each purchase (in 'conversions' table) has a certain revenue attached to it and was made by a given user ('user_id'). In the 'session_souces' table you can find information of what sessions (a session is a set of events) happened on the company's website. 
Every user who made a conversion, had multiple sessions prior to this purchase which make up his **customer journey**. The link between conversions and those sessions is made via the 'attribution_customer_journey' table where for each conv_id from the 'conversions' table, you can find all sessions that belong to this customer journey.

The 'conversions_backend' table is exactly the same as the 'conversions' table in terms of format but contains data directly from the company's backend system and is considered **true**. In case the data in the 'conversions' table differs from the data in the 'conversions_backend' table, this is an issue.  

Often there are external data sources (for instance for marketing costs) that come into play. In this case, there is one external data source **api_adwords_costs** table. This table contains per day and AdWords campaign ID the costs that Company X paid for running this ad.
The campaign_id here links to the campaign_id in the 'session_sources' table.


## Tables in the challenge.db file

* session_sources:
    * *session_id*: unique identifier of this session
    * *user_id*: user identifier
    * *event_date*: date when the session happened
    * *event_time*: time when the session happened
    * *channel_name*: traffic channel that started this session (e.g. 'Email')
    * *campaign_name*: advertising campaign name that started this session (e.g. 'adwords_campaign_123')
    * *campaign_id*: campaign identifier that started this session (not all sessions have a campaign_id)
    * *market*: regional market that this session belongs to (e.g. 'DE' for Germany) 
    * *cpc*: cost-per-click of this (this is how much was paid for this session, you can assume its in Euro)

* conversions:
    * *conv_id*: unique identifier of this conversion
    * *user_id*: user identifier
    * *conv_date *: date when the conversion happened
    * *market*: regional market that this conversion belongs to
    * *revenue*: conversion amount (i.e. how much revenue the company earned through this conversion, you can assume its in Euro)

* conversions_backend :
    * *conv_id*: unique identifier of this conversion
    * *user_id*: user identifier
    * *conv_date *: date when the conversion happened
    * *market*: regional market that this conversion belongs to
    * *revenue*: conversion amount

* api_adwords_costs :
    * *event_date*: date when the AdWords campaign was running 
    * *campaign_id *: campaign identifier
    * *cost*: amount that was spent on running this campaign on this day (assume its in Euro)
    * *clicks*: number of times a user clicked on this ad on the given day

* attribution_customer_journey :
    * *conv_id*: conversion identifier 
    * *session_id*: session identifier that belonged in the customer journey of the given conv_id
    * *ihc*: 'value' of the given session in the given customer journey (1 = 100%)

*Note: the sum of 'ihc' column in the 'attribution_customer_journey' should be equal to 1 (100%) for each 'conv_id'*

## Questions
* Are the costs in the 'api_adwords_costs' table fully covered in the 'session_sources' table? Any campaigns where you see issues?
* Are the conversions in the 'conversions' table stable over time? Any pattern?
* Double check conversions ('conversions' table) with backend ('conversions_backend' table), any issues?
* Are attribution results consistent? Do you find any conversions where the 'ihc' values don't make sense?
* (Bonus) Do we have an issue with channeling? Are the number of sessions per channel stable over time?
* (Bonus) Any other issues?

## Deliverable

- a report (e.g. Jupyter Notebook or Word document) that answers the questions above
- please explain your approach for each question and state any assumptions that you make and that are not mentioned in the challenge
- if you use charts/pivots to answer the questions, please include them as well in your report
- keep your results concise (maximum 3-4 pages of Word document), no need to mention findings unrelated to the questions above


## Note: We don't expect you to build THE perfect analysis and report here.
Our goal here is:
* See how you approach such a problem
* Get an idea of your skills
