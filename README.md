# ETL - Airflow 

## Introduction

This project is an ETL (Extract, Transform, Load) application using Apache Airflow and Docker-Compose. The Airflow DAG processes toll data by extracting information from various file formats, consolidating it, and transforming the data.

## Project Structure

```
project-directory/
├── docker-compose.yml
├── dags/
│   └── etl_toll_data.py
├── data/
│   └── tolldata.tgz
└── README.md
```

## Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/NaveedAhmed55/etl-airflow.git
   cd project-directory
   ```

2. **Prepare the Environment:**
   Ensure Docker and Docker-Compose are installed. Refer to the [Docker documentation](https://docs.docker.com/get-docker/) for installation.

3. **Start the Airflow Services:**
   ```bash
   docker-compose up -d --build
   ```

4. **Access the Airflow Web UI:**
   Navigate to `http://localhost:8080` in your browser. Use the default credentials (username: `airflow`, password: `airflow`).

5. **Trigger the DAG:**
   In the Airflow UI, manually trigger the `ETL_toll_data_12` DAG to start the ETL process.

## Airflow DAG Description

The DAG `ETL_toll_data_01` runs daily and performs the following tasks:

1. **Unzip Data:** Extracts `tolldata.tgz` to the destination directory.
2. **Extract Data from CSV:** Processes and extracts specific columns from a CSV file.
3. **Extract Data from TSV:** Processes and extracts specific columns from a TSV file.
4. **Extract Data from Fixed Width File:** Processes and extracts specific columns from a fixed-width text file.
5. **Consolidate Data:** Merges the extracted data into a single CSV file.
6. **Transform Data:** Converts specific columns to uppercase in the consolidated CSV file.
