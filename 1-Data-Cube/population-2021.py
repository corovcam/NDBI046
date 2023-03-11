#!/usr/bin/env python3
import pandas as pd
import numpy as np

from rdflib import Graph, BNode, Literal, Namespace 
from rdflib.namespace import RDF, QB, XSD, SKOS, DCTERMS, OWL
from pandas.errors import SettingWithCopyWarning
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)


NS = Namespace("https://ndbi046-martincorovcak.com/ontology#")
NSR = Namespace("https://ndbi046-martincorovcak.com/resources/")
# We use custom Namespace here as the generated is limited in content
# https://rdflib.readthedocs.io/en/stable/_modules/rdflib/namespace/_RDFS.html
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
SDMX_CONCEPT = Namespace("http://purl.org/linked-data/sdmx/2009/concept#")
SDMX_MEASURE = Namespace("http://purl.org/linked-data/sdmx/2009/measure#")
SDMX_CODE = Namespace("http://purl.org/linked-data/sdmx/2009/code#")


def load_csv_file_as_object(file_path: str):
    result = pd.read_csv(file_path, low_memory=False)
    result = result.loc[result["vuk"] == "DEM0004"] # mean population data only
    return result


def set_region_per_county(data: pd.DataFrame):
    result = data.loc[data.vuzemi_cis == 101]
    
    care_providers_df = pd.read_csv("./care-providers/narodni-registr-poskytovatelu-zdravotnich-sluzeb.csv", 
                                    usecols=["Kraj", "KrajCode", "OkresCode"])
    care_providers_df = care_providers_df.drop_duplicates("OkresCode").dropna(subset="OkresCode")

    county_mapping_df = pd.read_csv("./population-2021/číselník-okresů-vazba-101-nadřízený.csv", usecols=["CHODNOTA1", "CHODNOTA2"])

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
    
    create_concept_schemes(result)
    create_resource_classes(result)
    create_resources(result, data)
    dimensions = create_dimensions(result)
    measures = create_measure(result)
    structure = create_structure(result, dimensions, measures)
    dataset = create_dataset(result, structure)
    create_observations(result, dataset, data)
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


def main():
    file_path = "./population-2021/130141-22data2021.csv"
    data = load_csv_file_as_object(file_path)
    data = set_region_per_county(data)
    data_cube = as_data_cube(data)
    data_cube.serialize(format="ttl", destination="population-2021.ttl")


if __name__ == "__main__":
    main()
