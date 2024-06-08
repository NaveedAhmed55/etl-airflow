from datetime import timedelta
import tarfile
import os
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
import psycopg2
import csv

import pandas as pd


default_args = {
    'owner': 'naveed',
    'email': 'dummy@gmail.com',
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

@dag(
    dag_id='ETL_toll_data_17', 
    default_args=default_args, 
    start_date=days_ago(0),
    schedule_interval='@daily',
    description='ETL-PIPELINE'
)
def hello_world_etl():

    #unzip the downloaded tgz
    @task()
    def unzip_data(source: str, destination: str):
        try:
            with tarfile.open(source, "r:gz") as tgz:
                tgz.extractall(destination)
            print(f"Successfully extracted {source} to {destination}")
        except Exception as e:
            print(f"Error extracting {source}: {e}")

    @task()
    def extract_data_from_csv(infile, outfile):
        try:
            with open(infile, "r") as readfile, open(outfile, "w") as writefile:
                for line in readfile:
                    columns = line.strip().split(",")
                    selected_columns = columns[0], columns[1], columns[2], columns[3]
                    selected_line = ",".join(selected_columns)
                    writefile.write(selected_line + "\n")
        except Exception as e:
            print(f"Error processing {infile}: {e}")

    @task()
    def extract_data_from_tsv(infile, outfile):
        try:
            with open(infile, 'r') as readfile, open(outfile, 'w') as writefile:
                for line in readfile:
                    columns = line.strip().split('\t')
                    selected_columns = columns[4], columns[5], columns[6]
                    selected_line = ",".join(selected_columns)
                    writefile.write(selected_line + "\n")
        except Exception as e:
            print(f"Error while processing {infile}: {e}")

    @task()
    def extract_data_from_fixed_width(infile, outfile):
        try:
            with open(infile, 'r') as readfile, open(outfile, 'w') as writefile:
                for line in readfile:
                    clean_line = ' '.join(line.strip().split())
                    columns = clean_line.split(' ')
                    select_columns = columns[9], columns[10]
                    selected_line = ','.join(select_columns)
                    writefile.write(selected_line + '\n')
                        
        except Exception as e:
            print(f"Error while processing file {infile} : {e}")

    @task()
    def consolidate_data(infile,outfile):
        try:
            combined_csv = pd.concat([pd.read_csv(f) for f in infile], axis=1)
            combined_csv.to_csv(outfile, index=False)
        except Exception as e:
            print(f"error while processing {infile} : {e}")
    @task()
    def transform_data(infile,outfile):
        df=pd.read_csv(infile)
        df.iloc[:,3]=df.iloc[:,3].str.upper()
        df.to_csv(outfile,index=False)

    @task()
    def load_to_database():
        #configure connection  to postgresql database
        dbname='airflow'
        user='airflow'
        password='airflow'
        host='db'
        port='5432'

        try:
            conn= psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                port=port,
                host=host
            )
            print("database connected successfully")
            cursor=conn.cursor()
            create_table_query = """
                CREATE TABLE IF NOT EXISTS VEHICLE_DATA(
                ID VARCHAR(50),
                Timestamp VARCHAR(50),
                Anonymized_Vehicle_number VARCHAR(50),
                Vehicle_type VARCHAR(50),
                Number_of_axles VARCHAR(50),
                Tollplaza_ID VARCHAR(50),
                Tollplaza_CODE VARCHAR(50),
                Type_of_Payment_code VARCHAR(50),
                Vehicle_code VARCHAR(50)
                )
            """
            cursor.execute(create_table_query)
            conn.commit()

            with open(transformed_data_output, 'r') as csvfile:
                for line in csvfile:
                    row = line.strip().split(',')  
                    cursor.execute(
                        "INSERT INTO VEHICLE_DATA (ID, Timestamp, Anonymized_Vehicle_number, Vehicle_type, Number_of_axles, Tollplaza_ID, Tollplaza_CODE, Type_of_Payment_code, Vehicle_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        row
                    )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error while connect to database {dbname} {e}")

    DESTINATION = "/opt/airflow/ds"
    source = os.path.join(DESTINATION, "tolldata.tgz")

    # input files paths
    vehicle_data = os.path.join(DESTINATION, "vehicle-data.csv")
    tollplaza_data = os.path.join(DESTINATION, "tollplaza-data.tsv")
    payment_data = os.path.join(DESTINATION, "payment-data.txt")


    # output files paths
    vehicle_data_output = os.path.join(DESTINATION, "csv_data.csv")
    tollplaza_data_output = os.path.join(DESTINATION, "tsv_data.csv")
    payment_data_output= os.path.join(DESTINATION, "fixed_width_data.csv")
    infiles=[vehicle_data_output,tollplaza_data_output,payment_data_output]
    combined_file=os.path.join(DESTINATION, "extracted_data.csv")
    transformed_data_output=os.path.join(DESTINATION, "transformed_data.csv")




    unzip_task = unzip_data(source, DESTINATION)
    extract_csv_task = extract_data_from_csv(vehicle_data, vehicle_data_output)
    extract_tsv_task = extract_data_from_tsv(tollplaza_data, tollplaza_data_output)
    extract_data_from_fixed_width_task=extract_data_from_fixed_width(payment_data,payment_data_output)
    consolidate_data_task=consolidate_data(infiles,combined_file)
    transform_data_task=transform_data(combined_file,transformed_data_output)
    load_to_database_task=load_to_database()

    # Dag pipeline definition
    unzip_task >> [extract_csv_task,extract_tsv_task,extract_data_from_fixed_width_task] >> consolidate_data_task >> transform_data_task>> load_to_database_task
    
 
greet_dag = hello_world_etl()
