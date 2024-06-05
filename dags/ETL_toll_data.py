from datetime import timedelta
import tarfile
import os
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'naveed',
    'email': 'naveedcodes@gmail.com',
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

@dag(
    dag_id='ETL_toll_data_01', 
    default_args=default_args, 
    start_date=days_ago(0),
    schedule_interval='@daily',
    description='Final Assignment'
)
def hello_world_etl():

    @task()
    def unzip_data(source: str, destination: str):
        """
        Extracts the contents of the source dataset .tgz file to the specified
        destination directory.

        Args:
            source (str): Path to the source .tgz file.
            destination (str): Directory where the contents will be extracted.
        """
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
                    selected_columns = columns[0], columns[1], columns[2], columns[3], columns[-1]
                    selected_line = ",".join(selected_columns)
                    writefile.write(selected_line + "\n")
        except Exception as e:
            print(f"Error processing {infile}: {e}")

    DESTINATION = "/opt/airflow/ds"
    source = os.path.join(DESTINATION, "tolldata.tgz")
    
    inputfile="/opt/airflow/ds/vehicle-data.csv"
    outputfile='/opt/airflow/ds/csv_data.csv'
    unzip_data=unzip_data(source, DESTINATION)
    extract_data_from_csv=extract_data_from_csv(inputfile,outputfile)
    
    unzip_data >> extract_data_from_csv

greet_dag = hello_world_etl()
