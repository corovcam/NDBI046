# NDBI046 - Assignment Solutions
Assignments solution repository for Introduction to Data Engineering class of 2022/2023.

## 1. Assignment: Data Cubes

Assignment specification: https://skoda.projekty.ms.mff.cuni.cz/ndbi046/seminars/02-data-cube.html#/3

1. Datacube
    - "Národní registr poskytovatelů zdravotních služeb"
    - Dataset URL: https://data.gov.cz/datov%C3%A1-sada?iri=https://data.gov.cz/zdroj/datov%C3%A9-sady/https---opendata.mzcr.cz-api-3-action-package_show-id-nrpzs
2. Datacube
    - "Pohyb obyvatel za ČR, kraje, okresy, SO ORP a obce - rok 2021"
    - Dataset URL: https://data.gov.cz/datov%C3%A1-sada?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatov%C3%A9-sady%2F00025593%2F12032e1445fd74fa08da79b14137fc29

#### System Requirements
- Python 3 (tested using Python 3.10.*)
- Modules (declared in [requirements.txt](1-Data-Cube/requirements.txt)):
  - [Pandas](https://pandas.pydata.org/) (for .csv transformation)
  - [NumPy](https://numpy.org/doc/stable/)
  - [RDFLib](https://rdflib.readthedocs.io/en/stable/index.html)

#### Installation & Instructions
1. Clone the repository
2. Navigate to "1-data-cube" directory
3. Install dependencies using `pip install -r requirements.txt`
4. Run respective RDF Turtle generation scripts using `python3 care-providers.py` and `python3 population-2021.py`
    - Check generated *care-providers.ttl* and *population-2021.ttl*
1. Check their validity using [*Integrity Constraints*](https://www.w3.org/TR/vocab-data-cube/#wf-rules) by running `python3 integrity-constraints.py`

#### Scripts Information

Scripts and Datasets are located in the [1-Data-Cube](1-Data-Cube) directory.

1. [care-providers.py](1-Data-Cube/care-providers.py)
    - Script uses [narodni-registr-poskytovatelu-zdravotnich-sluzeb.csv](care-providers/narodni-registr-poskytovatelu-zdravotnich-sluzeb.csv) for data transformation to obtain a valid [*Data Cube*](https://www.w3.org/TR/vocab-data-cube/)
      - Data Cube specs:
        - Dimension: county (okres)
        - Dimension: region (kraj)
        - Dimension: field of care (obor péče)
        - Measure: number of care providers per county (počet poskytovatelů péče)
2. [population-2021.py](1-Data-Cube/population-2021.py)
    - Script uses [130141-22data2021.csv](population-2021/130141-22data2021.csv) (Population counts per County/Region) for data transformation to obtain a valid [*Data Cube*](https://www.w3.org/TR/vocab-data-cube/)
      - Data Cube specs:
        - Dimension: county (okres)
        - Dimension: region (kraj)
        - Measure: mean population per county (střední stav obyvatel)
3. [integrity-constraints.py](1-Data-Cube/integrity-constraints.py)
    - Script uses pre-generated *care-providers.ttl* and *population-2021.ttl* RDF files to validate Data Cubes
    - If all tests "IC1" to "IC21" pass (returns *false*), then the respective Data Cube is valid


## 2. Assignment: Apache Airflow

Assignment specification: https://skoda.projekty.ms.mff.cuni.cz/ndbi046/seminars/03-airflow.html#/1/1

All generated *Data Cubes* are left unchanged from the [1. Assignment](#1-assignment-data-cubes).

#### System Requirements
- Docker (at least 4GB of memory)
- Docker Compose v1.29.1 or newer
- Modules (installed automatically with docker compose; declared in [requirements.txt](2-Apache-Airflow/airflow/requirements.txt)):
  - [Pandas](https://pandas.pydata.org/) (for .csv transformation)
  - [NumPy](https://numpy.org/doc/stable/)
  - [RDFLib](https://rdflib.readthedocs.io/en/stable/index.html)
  - [Requests](https://requests.readthedocs.io/en/latest/)

#### Installation & Instructions
1. Clone the repository
2. Navigate to "2-Apache-Airflow/airflow/" directory
3. Run `docker compose up --build`
4. Check out: [Apache Airflow - Docker Compose tutorial](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html) - all default settings are left unchanged
  - Only custom *requirements.txt" are set - check out: [Apache Airflow - adding dependencies to image](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#special-case-adding-dependencies-via-requirements-txt-file)
5. Check out the local Airflow WebServer using [http://localhost:8080/dags/data-cubes/](http://localhost:8080/dags/data-cubes/) and run the *DAG with Config* with "output_path" JSON parameter set to absolute path in linux filesystem (e.g. `{"output_path": "/opt/airflow/dags/"}`)
6. Run `docker compose down --volumes --rmi all` to stop and delete containers, delete volumes with database data and download images. (redownloads images at next `docker compose up --build`)

#### Scripts Information

DAGs are located in the [2-Apache-Airflow/airflow/](2-Apache-Airflow/airflow/dags) directory. Scripts to generate Data Cubes are the same as in the [1. Assignment](#1-assignment-data-cubes). The only thing changed is the custom *output_path* for .ttl files.


## 3. Assignment: Provenance

Assignment specification: https://skoda.projekty.ms.mff.cuni.cz/ndbi046/seminars/04-provenance.html#/1/1

All generated *Data Cubes* are left unchanged from the [1. Assignment](#1-assignment-data-cubes).

#### System Requirements
- Python 3 (tested using Python 3.10.*)
- Modules (declared in [requirements.txt](3-Provenance/requirements.txt)):
  - [RDFLib](https://rdflib.readthedocs.io/en/stable/index.html)

#### Installation & Instructions
1. Clone the repository
2. Navigate to "3-Provenance/" directory
3. Install dependencies using `pip install -r requirements.txt`
4. Run respective RDF TriG generation scripts using `python3 care_providers_prov.py` and `python3 population_2021_prov.py`
    - Check generated *care-providers-prov.trig* and *population-2021-prov.trig*
5. If you want the respective .ttl data cube files in the same directory, generate them using [1. Assignment](#1-assignment-data-cubes) and move them to the same directory as the .trig files

#### Scripts Information

1. [care_providers_prov.py](3-Provenance/care_providers_prov.py)
    - Script uses the [PROV](https://www.w3.org/TR/prov-overview/) ontology to generate a [RDF TriG](https://www.w3.org/TR/trig/) file with provenance information describing the data transformation from the [original .csv file](1-Data-Cube/care-providers/narodni-registr-poskytovatelu-zdravotnich-sluzeb.csv) to the [generated .ttl file](1-Data-Cube/care-providers.ttl)
2. [population_2021_prov.py](3-Provenance/population_2021_prov.py)
    - Script uses the [PROV](https://www.w3.org/TR/prov-overview/) ontology to generate a [RDF TriG](https://www.w3.org/TR/trig/) file with provenance information describing the data transformation from the [original .csv file](1-Data-Cube/population-2021/130141-22data2021.csv) to the [generated .ttl file](1-Data-Cube/population-2021.ttl)


## 4. Assignment: Dataset Metadata

Assignment specification: https://skoda.projekty.ms.mff.cuni.cz/ndbi046/seminars/05-vocabulary.html#/1

Generated *Population 2021 Data Cube* is left unchanged from the [1. Assignment](#1-assignment-data-cubes), except that the Region/County Codelist is extracted to a separate file.

#### System Requirements
- Python 3 (tested using Python 3.10.11)
- Modules (declared in [requirements.txt](1-Data-Cube/requirements.txt)):
  - [Pandas](https://pandas.pydata.org/) (for .csv transformation)
  - [NumPy](https://numpy.org/doc/stable/)
  - [RDFLib](https://rdflib.readthedocs.io/en/stable/index.html)

#### Installation & Instructions
1. Clone the repository
2. Navigate to [4-Metadata/](4-Metadata/) directory
3. Install dependencies using `pip install -r requirements.txt`
4. Run `python3 dataset_entry.py`
5. Check generated *population.ttl* (Data Cube file), *region-county-codelist.ttl* and *population-dataset-entry.ttl* files

#### Script Information

1. [dataset_entry.py](4-Metadata/dataset_entry.py)
    - Script uses the [DCAT](https://www.w3.org/TR/vocab-dcat-2/) ontology to generate a [RDF Turtle](https://www.w3.org/TR/turtle/) file with metadata describing the Population 2021 Data Cube
    - The script also generates a separate file with the Region/County Codelist
    - The script also generates a separate file with the original Population 2021 Data Cube