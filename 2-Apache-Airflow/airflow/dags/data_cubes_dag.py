import requests
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from operators.care_providers import process_care_providers
from operators.population_2021 import process_population

def consumer_operator(consumer, **kwargs):
    output_path = kwargs['dag_run'].conf.get("output_path", None)
    if output_path:
        consumer(output_path)
    else:
        consumer()

def get_dataset(url, verify_ssl = True):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True, verify=verify_ssl) as stream:
        stream.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in stream.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename

dag_args = {
    "email": ["airflowadmin@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    'retry_delay': timedelta(minutes=15)
}

with DAG(
    dag_id="data-cubes",
    default_args=dag_args,
    start_date=datetime(2023, 3, 20),
    schedule=None,
    catchup=False,
    tags=["NDBI046"],
) as dag:
    
    # Care Providers
    
    t1 = PythonOperator(
        task_id="get-care-providers-dataset",
        python_callable=get_dataset,
        op_args=["https://opendata.mzcr.cz/data/nrpzs/narodni-registr-poskytovatelu-zdravotnich-sluzeb.csv"]
    )
    t1.doc_md = """\
    Downloads the **Národní registr poskytovatelů zdravotních služeb** dataset from OpenData MZČR website.
    """
    
    t2 = PythonOperator(
        task_id="care-providers-etl",
        python_callable=consumer_operator,
        op_args=[process_care_providers]
    )
    t2.doc_md = """\
    Runs the Extract-Transform-Load process on **Care Providers** dataset and generates RDF Turtle file in a location specified with `output_path` DAG Run parameter.
    """
    
    # Population 2021
    
    t3 = PythonOperator(
        task_id="get-population-2021-dataset",
        python_callable=get_dataset,
        op_args=["https://www.czso.cz/documents/10180/184344914/130141-22data2021.csv"]
    )
    t3.doc_md = """\
    Downloads the **Pohyb obyvatel za ČR, kraje, okresy, SO ORP a obce - rok 2021** dataset from OpenData MZČR website.
    """
    
    t4 = PythonOperator(
        task_id="get-county-codelist-dataset",
        python_callable=get_dataset,
        op_args=[
            "https://skoda.projekty.ms.mff.cuni.cz/ndbi046/seminars/02/číselník-okresů-vazba-101-nadřízený.csv", 
            False
        ]
    )
    t4.doc_md = """\
    Downloads the **Vazba mezi číselníky ČSÚ: OKRES_LAU (kód 109) - OKRES_NUTS (kód 101)** dataset from *NDBI046* course website.
    """
    
    t5 = PythonOperator(
        task_id="population-2021-etl",
        python_callable=consumer_operator,
        op_args=[process_population]
    )
    t5.doc_md = """\
     Runs the Extract-Transform-Load process on **Population 2021** dataset and generates RDF Turtle file in a location specified with `output_path` DAG Run parameter.
     """

    t1 >> t2
    [t1, t3, t4] >> t5
    