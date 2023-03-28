#!/usr/bin/env python3

from rdflib import Graph, Literal, Namespace, URIRef, BNode
from rdflib.namespace import RDF, FOAF, XSD, PROV

NSR = Namespace("https://ndbi046-martincorovcak.com/resources/")
NSP = Namespace("https://ndbi046-martincorovcak.com/provenance#")


def get_prov_data() -> Graph:
    result = Graph(bind_namespaces="rdflib")
    
    create_entities(result)
    create_agents(result)
    create_activities(result)
    
    create_auxiliary_resources(result)

    return result


def create_entities(collector: Graph):
    data_cube = NSR.MeanPopulation2021
    collector.add((data_cube, RDF.type, PROV.Entity))
    collector.add((data_cube, PROV.wasGeneratedBy, NSP.Population2021CubeCreationActivity))
    collector.add((data_cube, PROV.wasDerivedFrom, NSP.Population2021Dataset))
    collector.add((data_cube, PROV.wasAttributedTo, NSP.Population2021ETLScript))
    
    population_2021_dataset = NSP.Population2021Dataset
    collector.add((population_2021_dataset, RDF.type, PROV.Entity))
    collector.add((population_2021_dataset, PROV.wasAttributedTo, NSP.CzechStatisticalOffice))
    
    care_providers_dataset = NSP.CareProvidersDataset
    collector.add((care_providers_dataset, RDF.type, PROV.Entity))
    collector.add((care_providers_dataset, PROV.wasAttributedTo, NSP.MinistryOfHealthCR))
    
    county_codelist_map = NSP.CountyCodelistMap
    collector.add((county_codelist_map, RDF.type, PROV.Entity))
    collector.add((county_codelist_map, PROV.wasAttributedTo, NSP.CzechStatisticalOffice))
    

def create_agents(collector: Graph):
    script = NSP.Population2021ETLScript
    collector.add((script, RDF.type, PROV.SoftwareAgent))
    collector.add((script, PROV.actedOnBehalfOf, NSP.MartinCorovcak))
    collector.add((script, PROV.atLocation, URIRef("file://population_2021.py")))
    
    author = NSP.MartinCorovcak
    collector.add((author, RDF.type, FOAF.Person))
    collector.add((author, RDF.type, PROV.Agent))
    collector.add((author, PROV.actedOnBehalfOf, NSP.PetrSkoda))
    collector.add((author, FOAF.name, Literal("Martin Čorovčák", lang="sk")))
    collector.add((author, FOAF.mbox, URIRef("mailto:martino.coro@gmail.com")))
    collector.add((author, FOAF.homepage, Literal("https://github.com/corovcam", datatype=XSD.anyURI)))
    
    teacher = NSP.PetrSkoda
    collector.add((teacher, RDF.type, FOAF.Person))
    collector.add((teacher, RDF.type, PROV.Agent))
    collector.add((teacher, PROV.actedOnBehalfOf, NSP.MFF_UK))
    collector.add((teacher, FOAF.name, Literal("Mgr. Petr Škoda, Ph.D.", lang="cs")))
    collector.add((teacher, FOAF.mbox, URIRef("mailto:petr.skoda@matfyz.cuni.cz")))
    
    organization = NSP.MFF_UK
    collector.add((organization, RDF.type, FOAF.Organization))
    collector.add((organization, RDF.type, PROV.Agent))
    collector.add((organization, FOAF.name, Literal("Matematicko-fyzikální fakulta, Univerzita Karlova", lang="cs")))
    collector.add((organization, FOAF.schoolHomepage, Literal("https://www.mff.cuni.cz/", datatype=XSD.anyURI)))
    
    cz_stat_office = NSP.CzechStatisticalOffice
    collector.add((cz_stat_office, RDF.type, FOAF.Organization))
    collector.add((cz_stat_office, RDF.type, PROV.Agent))
    collector.add((cz_stat_office, FOAF.name, Literal("Český statistický úřad", lang="cs")))
    collector.add((cz_stat_office, FOAF.homepage, Literal("https://www.czso.cz/", datatype=XSD.anyURI)))
    
    ministry_of_health = NSP.MinistryOfHealthCR
    collector.add((ministry_of_health, RDF.type, FOAF.Organization))
    collector.add((ministry_of_health, RDF.type, PROV.Agent))
    collector.add((ministry_of_health, FOAF.name, Literal("Ministerstvo zdravotnictví ČR", lang="cs")))
    collector.add((ministry_of_health, FOAF.homepage, Literal("https://www.mzcr.cz/", datatype=XSD.anyURI)))
    

def create_activities(collector: Graph):
    dc_activity = NSP.Population2021CubeCreationActivity
    collector.add((dc_activity, RDF.type, PROV.Activity))
    collector.add((dc_activity, PROV.startedAtTime, Literal("2023-03-28T12:00:00", datatype=XSD.dateTime)))
    collector.add((dc_activity, PROV.endedAtTime, Literal("2023-03-28T12:05:00", datatype=XSD.dateTime)))
    collector.add((dc_activity, PROV.used, NSP.Population2021Dataset))
    collector.add((dc_activity, PROV.used, NSP.CareProvidersDataset))
    collector.add((dc_activity, PROV.used, NSP.CountyCodelistMap))
    collector.add((dc_activity, PROV.wasAssociatedWith, NSP.MartinCorovcak))
    
    usage1 = BNode()
    collector.add((dc_activity, PROV.qualifiedUsage, usage1))
    collector.add((usage1, RDF.type, PROV.Usage))
    collector.add((usage1, PROV.entity, NSP.Population2021Dataset))
    collector.add((usage1, PROV.hadRole, NSP.ETLRole))
    
    usage2 = BNode()
    collector.add((dc_activity, PROV.qualifiedUsage, usage2))
    collector.add((usage2, RDF.type, PROV.Usage))
    collector.add((usage2, PROV.entity, NSP.CareProvidersDataset))
    collector.add((usage2, PROV.hadRole, NSP.ETLRole))
    
    usage3 = BNode()
    collector.add((dc_activity, PROV.qualifiedUsage, usage3))
    collector.add((usage3, RDF.type, PROV.Usage))
    collector.add((usage3, PROV.entity, NSP.CountyCodelistMap))
    collector.add((usage3, PROV.hadRole, NSP.ETLRole))
    

def create_auxiliary_resources(collector: Graph):
    # Locations of data sources
    collector.add((URIRef("file://population_2021.py"), RDF.type, PROV.Location))
    
    # Roles
    # For simplicity let's assume that the ETL script has only 1 role
    collector.add((NSP.ETLRole, RDF.type, PROV.Role))


def create_prov_data(output_path = "."):
    """Create provenance data for the care providers dataset.

    Args:
        output_path (str, optional): Path to the output directory. Defaults to ".".
    """
    
    prov_data = get_prov_data()
    output_path = output_path.rstrip("/")
    prov_data.serialize(format="trig", destination = f"{output_path}/population-2021-prov.trig")


if __name__ == "__main__":
    create_prov_data()
