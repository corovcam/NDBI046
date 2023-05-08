#!/usr/bin/env python3
import pandas as pd
import numpy as np

from rdflib import Graph, Literal, Namespace 
from rdflib.namespace import RDF, SKOS, OWL
from pandas.errors import SettingWithCopyWarning
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)


NSR = Namespace("https://ndbi046-martincorovcak.com/resources/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
SDMX_CODE = Namespace("http://purl.org/linked-data/sdmx/2009/code#")


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


def process_data(data):
    result = Graph(bind_namespaces="rdflib")
    
    create_concept_schemes(result)
    create_resource_classes(result)
    create_resources(result, data)
    
    return result
    

def create_concept_schemes(collector: Graph):
    county = NSR.county
    collector.add((county, RDF.type, SKOS.ConceptScheme))
    collector.add((county, RDFS.label, Literal("Okres - číselník", lang="cs")))
    collector.add((county, RDFS.label, Literal("County - codelist", lang="en")))
    collector.add((county, SKOS.prefLabel, Literal("Okres - číselník", lang="cs")))
    collector.add((county, SKOS.prefLabel, Literal("County - codelist", lang="en")))
    collector.add((county, RDFS.seeAlso, NSR.County))
    
    region = NSR.region
    collector.add((region, RDF.type, SKOS.ConceptScheme))
    collector.add((region, RDFS.label, Literal("Kraj - číselník", lang="cs")))
    collector.add((region, RDFS.label, Literal("Region - codelist", lang="en")))
    collector.add((region, SKOS.prefLabel, Literal("Kraj - číselník", lang="cs")))
    collector.add((region, SKOS.prefLabel, Literal("Region - codelist", lang="en")))
    collector.add((region, RDFS.seeAlso, NSR.Region))


def create_resource_classes(collector: Graph):
    county = NSR.County
    collector.add((county, RDF.type, RDFS.Class))
    collector.add((county, RDF.type, OWL.Class))
    collector.add((county, RDFS.label, Literal("Okres", lang="cs")))
    collector.add((county, RDFS.label, Literal("County", lang="en")))
    collector.add((county, SKOS.prefLabel, Literal("Okres", lang="cs")))
    collector.add((county, SKOS.prefLabel, Literal("County", lang="en")))
    collector.add((county, RDFS.seeAlso, NSR.county))
    
    region = NSR.Region
    collector.add((region, RDF.type, RDFS.Class))
    collector.add((region, RDF.type, OWL.Class))
    collector.add((region, RDFS.label, Literal("Kraj", lang="cs")))
    collector.add((region, RDFS.label, Literal("Region", lang="en")))
    collector.add((region, SKOS.prefLabel, Literal("Kraj", lang="cs")))
    collector.add((region, SKOS.prefLabel, Literal("Region", lang="en")))
    collector.add((region, RDFS.seeAlso, NSR.region))


def create_resources(collector: Graph, data: pd.DataFrame):
    for _, c in data.iterrows():
        county = NSR[f"county/{c['okres_lau']}"]
        collector.add((county, RDF.type, SKOS.Concept))
        collector.add((county, RDF.type, SDMX_CODE.Area))
        collector.add((county, RDF.type, NSR.County))
        collector.add((county, RDFS.label, Literal(c["vuzemi_txt"], lang="cs")))
        collector.add((county, SKOS.prefLabel, Literal(c["vuzemi_txt"], lang="cs")))
        collector.add((county, SKOS.inScheme, NSR.county))
        collector.add((county, SKOS.inScheme, SDMX_CODE.area))
        collector.add((county, SKOS.notation, Literal(c["okres_lau"])))
    
    regions = data.drop_duplicates("kraj_kod")
    for _, r in regions.iterrows():
        region = NSR[f"region/{r['kraj_kod']}"]
        collector.add((region, RDF.type, SKOS.Concept))
        collector.add((region, RDF.type, SDMX_CODE.Area))
        collector.add((region, RDF.type, NSR.Region))
        collector.add((region, RDFS.label, Literal(r["kraj_txt"], lang="cs")))
        collector.add((region, SKOS.prefLabel, Literal(r["kraj_txt"], lang="cs")))
        collector.add((region, SKOS.inScheme, NSR.region))
        collector.add((region, SKOS.inScheme, SDMX_CODE.area))
        collector.add((region, SKOS.notation, Literal(r["kraj_kod"])))

    
def create_codelist(output_path = "."):
    file_path = "data/130141-22data2021.csv"
    data = load_csv_file_as_object(file_path)
    data = set_region_per_county(data)
    data_cube = process_data(data)
    data_cube.serialize(format="ttl", destination = output_path.rstrip("/") + "/region-county-codelist.ttl")


if __name__ == "__main__":
    create_codelist()
