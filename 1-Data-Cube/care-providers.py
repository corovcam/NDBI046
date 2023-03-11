#!/usr/bin/env python3
import pandas as pd
import numpy as np

from rdflib import Graph, BNode, Literal, Namespace 
from rdflib.namespace import RDF, QB, XSD, SKOS, DCTERMS, OWL

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
    
    field_of_care = NSR.fieldOfCare
    collector.add((field_of_care, RDF.type, SKOS.ConceptScheme))
    collector.add((field_of_care, RDFS.label, Literal("Obor péče - číselník", lang="cs")))
    collector.add((field_of_care, RDFS.label, Literal("Field of care - codelist", lang="en")))
    collector.add((field_of_care, SKOS.prefLabel, Literal("Obor péče - číselník", lang="cs")))
    collector.add((field_of_care, SKOS.prefLabel, Literal("Field of care - codelist", lang="en")))
    collector.add((field_of_care, RDFS.seeAlso, NSR.FieldOfCare))


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
    
    field_of_care = NSR.FieldOfCare
    collector.add((field_of_care, RDF.type, RDFS.Class))
    collector.add((field_of_care, RDF.type, OWL.Class))
    collector.add((field_of_care, RDFS.label, Literal("Obor péče", lang="cs")))
    collector.add((field_of_care, RDFS.label, Literal("Field of care", lang="en")))
    collector.add((field_of_care, SKOS.prefLabel, Literal("Obor péče", lang="cs")))
    collector.add((field_of_care, SKOS.prefLabel, Literal("Field of care", lang="en")))
    collector.add((field_of_care, RDFS.seeAlso, NSR.fieldOfCare))


def create_resources(collector: Graph, data: pd.DataFrame):
    counties = data.drop_duplicates("OkresCode")[["OkresCode", "Okres"]].dropna(subset="OkresCode")
    for _, c in counties.iterrows():
        county = NSR[f"county/{c['OkresCode']}"]
        collector.add((county, RDF.type, SKOS.Concept))
        collector.add((county, RDF.type, SDMX_CODE.Area))
        collector.add((county, RDF.type, NSR.County))
        collector.add((county, RDFS.label, Literal(c["Okres"], lang="cs")))
        collector.add((county, SKOS.prefLabel, Literal(c["Okres"], lang="cs")))
        collector.add((county, SKOS.inScheme, NSR.county))
        collector.add((county, SKOS.inScheme, SDMX_CODE.area))
    
    regions = data.drop_duplicates("KrajCode")[["KrajCode", "Kraj"]].dropna(subset="KrajCode")
    for _, r in regions.iterrows():
        region = NSR[f"region/{r['KrajCode']}"]
        collector.add((region, RDF.type, SKOS.Concept))
        collector.add((region, RDF.type, SDMX_CODE.Area))
        collector.add((region, RDF.type, NSR.Region))
        collector.add((region, RDFS.label, Literal(r["Kraj"], lang="cs")))
        collector.add((region, SKOS.prefLabel, Literal(r["Kraj"], lang="cs")))
        collector.add((region, SKOS.inScheme, NSR.region))
        collector.add((region, SKOS.inScheme, SDMX_CODE.area))
    
    fields_of_care = data["OborPece"].unique()
    foc_index = pd.Index(fields_of_care)
    data["OborPeceCode"] = data["OborPece"].apply(lambda x: foc_index.get_loc(x))
    for index in range(len(fields_of_care)):
        field_of_care = NSR[f"fieldOfCare/{index}"]
        collector.add((field_of_care, RDF.type, SKOS.Concept))
        collector.add((field_of_care, RDF.type, NSR.FieldOfCare))
        collector.add((field_of_care, RDFS.label, Literal(fields_of_care[index], lang="cs")))
        collector.add((field_of_care, SKOS.prefLabel, Literal(fields_of_care[index], lang="cs")))
        collector.add((field_of_care, SKOS.inScheme, NSR.fieldOfCare))


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

    field_of_care = NS.fieldOfCare
    collector.add((field_of_care, RDF.type, RDFS.Property))
    collector.add((field_of_care, RDF.type, QB.DimensionProperty))
    collector.add((field_of_care, RDF.type, QB.CodedProperty))
    collector.add((field_of_care, RDFS.label, Literal("Obor péče", lang="cs")))
    collector.add((field_of_care, RDFS.label, Literal("Field of care", lang="en")))
    collector.add((field_of_care, RDFS.range, NSR.FieldOfCare))
    collector.add((field_of_care, QB.codeList, NSR.fieldOfCare))

    return [county, region, field_of_care]


def create_measure(collector: Graph):
    num_of_care_providers = NS.numberOfCareProviders
    collector.add( ( num_of_care_providers, RDF.type, RDFS.Property ) )
    collector.add( ( num_of_care_providers, RDF.type, QB.MeasureProperty ) )
    collector.add( ( num_of_care_providers, RDFS.label, Literal("Počet poskytovatelů péče", lang="cs") ) )
    collector.add( ( num_of_care_providers, RDFS.label, Literal("Number of care providers", lang="en") ) )
    collector.add( (num_of_care_providers, RDFS.subPropertyOf, SDMX_MEASURE.obsValue) )
    collector.add( ( num_of_care_providers, RDFS.range, XSD.integer ) )

    return [num_of_care_providers]


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
    dataset = NSR.CareProviders
    collector.add((dataset, RDF.type, QB.DataSet))
    collector.add((dataset, RDFS.label, Literal("Poskytovatelé zdravotních služeb", lang="cs")))
    collector.add((dataset, RDFS.label, Literal("Care Providers", lang="en")))
    collector.add((dataset, DCTERMS.issued, Literal("2023-03-11", datatype=XSD.date)))
    collector.add((dataset, DCTERMS.modified, Literal("2023-03-12", datatype=XSD.date)))
    collector.add((dataset, DCTERMS.title, Literal("Poskytovatelé zdravotních služeb", lang="cs")))
    collector.add((dataset, DCTERMS.title, Literal("Care Providers", lang="en")))
    collector.add((dataset, DCTERMS.publisher, Literal("https://github.com/corovcam", datatype=XSD.anyURI)))
    collector.add((dataset, DCTERMS.license, Literal("https://github.com/corovcam/NDBI046/blob/main/LICENSE", datatype=XSD.anyURI)))
    collector.add((dataset, QB.structure, structure))

    return dataset


def create_observations(collector: Graph, dataset, data: pd.DataFrame):
    grouped = data.groupby(["OkresCode", "KrajCode", "OborPeceCode"]).size().reset_index(name="PocetPoskytovaluPece")
    for index, row in grouped.iterrows():
        resource = NSR["observation-" + str(index).zfill(4)]
        create_observation(collector, dataset, resource, row)


def create_observation(collector: Graph, dataset, resource, data):
    collector.add((resource, RDF.type, QB.Observation))
    collector.add((resource, QB.dataSet, dataset))
    collector.add((resource, NS.county, NSR[f"county/{data['OkresCode']}"]))
    collector.add((resource, NS.region, NSR[f"region/{data['KrajCode']}"]))
    collector.add((resource, NS.fieldOfCare, NSR[f"fieldOfCare/{data['OborPeceCode']}"]))
    collector.add((resource, NS.numberOfCareProviders, Literal(data["PocetPoskytovaluPece"], datatype=XSD.integer)))


def main():
    file_path = "./care-providers/narodni-registr-poskytovatelu-zdravotnich-sluzeb.csv"
    data = load_csv_file_as_object(file_path)
    data_cube = as_data_cube(data)
    data_cube.serialize(format="ttl", destination="care-providers.ttl")


if __name__ == "__main__":
    main()
