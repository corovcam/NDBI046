#!/usr/bin/env python3
import pandas as pd
import numpy as np

from rdflib import Graph, BNode, Literal, Namespace 
from rdflib.namespace import RDF, QB, XSD, DCTERMS
from pandas.errors import SettingWithCopyWarning
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)


NS = Namespace("https://ndbi046-martincorovcak.com/ontology#")
NSR = Namespace("https://ndbi046-martincorovcak.com/resources/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
SDMX_CONCEPT = Namespace("http://purl.org/linked-data/sdmx/2009/concept#")
SDMX_MEASURE = Namespace("http://purl.org/linked-data/sdmx/2009/measure#")


def load_csv_file_as_object(file_path: str):
    result = pd.read_csv(file_path, low_memory=False)
    result = result.loc[result["vuk"] == "DEM0004"] # mean population data only
    return result


def set_region_per_county(data: pd.DataFrame):
    result = data.loc[data.vuzemi_cis == 101]
    
    care_providers_df = pd.read_csv("data/narodni-registr-poskytovatelu-zdravotnich-sluzeb.csv", 
                                    usecols=["Kraj", "KrajCode", "OkresCode"])
    care_providers_df = care_providers_df.drop_duplicates(["OkresCode"]).dropna(subset=["OkresCode"])

    county_mapping_df = pd.read_csv("data/číselník-okresů-vazba-101-nadřízený.csv", usecols=["CHODNOTA1", "CHODNOTA2"])

    result["okres_lau"] = result["vuzemi_kod"].apply(
        lambda x: county_mapping_df.loc[county_mapping_df["CHODNOTA2"] == x]["CHODNOTA1"].values[0]
    )
    result["kraj_kod"] = result["okres_lau"].apply(
        lambda x: care_providers_df.loc[care_providers_df["OkresCode"] == x]["KrajCode"].values[0]
    )
    result["kraj_txt"] = result["okres_lau"].apply(
        lambda x: care_providers_df.loc[care_providers_df["OkresCode"] == x]["Kraj"].values[0]
    )
    
    return result


def as_data_cube(data):
    result = Graph(bind_namespaces="rdflib")
    
    dimensions = create_dimensions(result)
    measures = create_measure(result)
    structure = create_structure(result, dimensions, measures)
    dataset = create_dataset(result, structure)
    create_observations(result, dataset, data)
    return result


def create_dimensions(collector: Graph):
    county = NS.county
    collector.add((county, RDF.type, RDFS.Property))
    collector.add((county, RDF.type, QB.DimensionProperty))
    collector.add((county, RDF.type, QB.CodedProperty))
    collector.add((county, RDFS.label, Literal("Okres", lang="cs")))
    collector.add((county, RDFS.label, Literal("County", lang="en")))
    collector.add((county, RDFS.range, NSR.County))
    collector.add((county, QB.codeList, NSR.county))
    collector.add((county, QB.concept, SDMX_CONCEPT.refArea))

    region = NS.region
    collector.add((region, RDF.type, RDFS.Property))
    collector.add((region, RDF.type, QB.DimensionProperty))
    collector.add((region, RDF.type, QB.CodedProperty))
    collector.add((region, RDFS.label, Literal("Kraj", lang="cs")))
    collector.add((region, RDFS.label, Literal("Region", lang="en")))
    collector.add((region, RDFS.range, NSR.Region))
    collector.add((region, QB.codeList, NSR.region))
    collector.add((region, QB.concept, SDMX_CONCEPT.refArea))

    return [county, region]


def create_measure(collector: Graph):
    mean_population = NS.meanPopulation
    collector.add( ( mean_population, RDF.type, RDFS.Property ) )
    collector.add( ( mean_population, RDF.type, QB.MeasureProperty ) )
    collector.add( ( mean_population, RDFS.label, Literal("Střední stav obyvatel - počet", lang="cs") ) )
    collector.add( ( mean_population, RDFS.label, Literal("Mean population count", lang="en") ) )
    collector.add( ( mean_population, RDFS.subPropertyOf, SDMX_MEASURE.obsValue ) )
    collector.add( ( mean_population, RDFS.range, XSD.integer ) )

    return [mean_population]


def create_structure(collector: Graph, dimensions, measures):
    structure = NS.structure
    collector.add( ( structure, RDF.type, QB.DataStructureDefinition ) )

    for dimension in dimensions:
        component = BNode()
        collector.add((structure, QB.component, component))
        collector.add((component, QB.dimension, dimension))

    for measure in measures:
        component = BNode()
        collector.add((structure, QB.component, component))
        collector.add((component, QB.measure, measure))

    return structure


def create_dataset(collector: Graph, structure):
    dataset = NSR.MeanPopulation2021
    collector.add((dataset, RDF.type, QB.DataSet))
    collector.add((dataset, RDFS.label, Literal("Střední stav obyvatel v Okresech 2021", lang="cs")))
    collector.add((dataset, RDFS.label, Literal("Mean Population per County 2021", lang="en")))
    collector.add((dataset, DCTERMS.issued, Literal("2023-03-11", datatype=XSD.date)))
    collector.add((dataset, DCTERMS.modified, Literal("2023-03-12", datatype=XSD.date)))
    collector.add((dataset, DCTERMS.title, Literal("Střední stav obyvatel v Okresech 2021", lang="cs")))
    collector.add((dataset, DCTERMS.title, Literal("Mean Population per County 2021", lang="en")))
    collector.add((dataset, DCTERMS.publisher, Literal("https://github.com/corovcam", datatype=XSD.anyURI)))
    collector.add((dataset, DCTERMS.license, Literal("https://github.com/corovcam/NDBI046/blob/main/LICENSE", datatype=XSD.anyURI)))
    collector.add((dataset, QB.structure, structure))

    return dataset


def create_observations(collector: Graph, dataset, data: pd.DataFrame):
    mean_population_data = data.reset_index()
    for index, row in mean_population_data.iterrows():
        resource = NSR["observation-" + str(index).zfill(2)]
        create_observation(collector, dataset, resource, row)


def create_observation(collector: Graph, dataset, resource, data):
    collector.add((resource, RDF.type, QB.Observation))
    collector.add((resource, QB.dataSet, dataset))
    collector.add((resource, NS.county, NSR[f"county/{data['okres_lau']}"]))
    collector.add((resource, NS.region, NSR[f"region/{data['kraj_kod']}"]))
    collector.add((resource, NS.meanPopulation, Literal(data["hodnota"], datatype=XSD.integer)))

    
def process_population(output_path = "."):
    file_path = "data/130141-22data2021.csv"
    data = load_csv_file_as_object(file_path)
    data = set_region_per_county(data)
    data_cube = as_data_cube(data)
    data_cube.serialize(format="ttl", destination = output_path.rstrip("/") + "/population.ttl")


if __name__ == "__main__":
    process_population()
