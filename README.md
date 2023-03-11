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