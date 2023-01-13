import pandas as pd
import sqlite3
import requests
from airflow import DAG
from datetime import timedelta
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator

CONN = sqlite3.connect('test.db')

def extract_data(url, tmp_file):
  pd.read_csv(url).to_csv(tmp_file)

def insert_to_db(tmp_file, table_name, conn=CONN):
  data = pd.read_csv(tmp_file)
  data.to_sql(table_name, conn, if_exists='replace', index=False)

def sql_query(sql,conn=CONN):
  cursor=conn.cursor()
  cursor.execute(sql)
  record=cursor.fetchall()
  cursor.close()

sql_query('CREATE TABLE if not exists join_data (date DATE, code TEXT,currency TEXT, start_date DATE, end_date DATE, value NUMERIC)')


with DAG(dag_id='dag',
        schedule_interval='*/5 * * * *',
        start_date=days_ago(1)
  ) as dag:

  extract_currency=PythonOperator(
      task_id='extract_currency',
      python_callable=extract_data,
      op_kwargs={
          'url': 'https://api.exchangerate.host/timeseries?start_date=2021-01-01&end_date=2021-01-01&base=EUR&symbols=USD&format=CSV',
          'tmp_file': '/tmp/currencydata.csv'}
  )
  extract_data=PythonOperator(
      task_id='extract_data',
      python_callable=extract_data,
      op_kwargs={
          'url': 'https://github.com/dm-novikov/stepik_airflow_course/blob/main/data_new/2021-01-01.csv?raw=true',
          'tmp_file': '/tmp/daydata.csv'
      }
  )
  insert_data=PythonOperator(
      task_id='insert_data',
      python_callable=insert_to_db,
      op_kwargs={
          'tmp_file' : '/tmp/daydata.csv',
          'table_name' : 'data'
      }
  )
  insert_currency=PythonOperator(
      task_id='insert_currency',
      python_callable=insert_to_db,
      op_kwargs={
          'tmp_file' : '/tmp/currencydata.csv',
          'table_name' : 'currency'
          }
  )
  join_data=PythonOperator(
      task_id='join_data',
      python_callable = sql_query,
      op_kwargs = {
          'sql' : 'INSERT OR REPLACE INTO join_data select d.date, c.code, d.currency, c.start_date, c.end_date, d.value from currency as c inner join data as d on c.date=d.date and c.base=d.currency'
      }
  )
  extract_currency>>insert_currency
  extract_data>>insert_data
  [insert_currency,insert_data]>>join_data