# AirflowProject
This repository contains an ETL pipeline which was built using Airflow framework

Here a list of libraries that are used: requests, pandas, airlow, datetime

First of all, we create sqlite connection to test database. Next, we have to create extract, transform and load function for a future usage. 
Finally, we use Aiflows's DAG to set up schedule and pass our ETL functions through Operators. Lastly, we create an order for tasks with streams 
