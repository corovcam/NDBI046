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
    data_cube = NSR.CareProviders
    collector.add((data_cube, RDF.type, PROV.Entity))
    collector.add((data_cube, PROV.wasGeneratedBy, NSP.CareProvidersCubeCreationActivity))
    collector.add((data_cube, PROV.wasDerivedFrom, NSP.CareProvidersDataset))
    collector.add((data_cube, PROV.wasAttributedTo, NSP.CareProvidersETLScript))
    
    dataset = NSP.CareProvidersDataset
    collector.add((dataset, RDF.type, PROV.Entity))
    collector.add((dataset, PROV.wasAttributedTo, NSP.MinistryOfHealthCR))
    

def create_agents(collector: Graph):
    script = NSP.CareProvidersETLScript
    collector.add((script, RDF.type, PROV.SoftwareAgent))
    collector.add((script, PROV.actedOnBehalfOf, NSP.MartinCorovcak))
    collector.add((script, PROV.atLocation, URIRef("file://care_providers.py")))
    
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
    
    ministry_of_health = NSP.MinistryOfHealthCR
    collector.add((ministry_of_health, RDF.type, FOAF.Organization))
    collector.add((ministry_of_health, RDF.type, PROV.Agent))
    collector.add((ministry_of_health, FOAF.name, Literal("Ministerstvo zdravotnictví ČR", lang="cs")))
    collector.add((ministry_of_health, FOAF.homepage, Literal("https://www.mzcr.cz/", datatype=XSD.anyURI)))
    

def create_activities(collector: Graph):
    dc_activity = NSP.CareProvidersCubeCreationActivity
    collector.add((dc_activity, RDF.type, PROV.Activity))
    collector.add((dc_activity, PROV.startedAtTime, Literal("2023-03-28T12:00:00", datatype=XSD.dateTime)))
    collector.add((dc_activity, PROV.endedAtTime, Literal("2023-03-28T12:05:00", datatype=XSD.dateTime)))
    collector.add((dc_activity, PROV.used, NSP.CareProvidersDataset))
    collector.add((dc_activity, PROV.wasAssociatedWith, NSP.MartinCorovcak))
    
    usage = BNode()
    collector.add((dc_activity, PROV.qualifiedUsage, usage))
    collector.add((usage, RDF.type, PROV.Usage))
    collector.add((usage, PROV.entity, NSP.CareProvidersDataset))
    collector.add((usage, PROV.hadRole, NSP.ETLRole))
    

def create_auxiliary_resources(collector: Graph):
    # Locations of data sources
    collector.add((URIRef("file://care_providers.py"), RDF.type, PROV.Location))
    
    # Roles
    collector.add((NSP.ETLRole, RDF.type, PROV.Role))


def create_prov_data(output_path = "."):
    """Create provenance data for the care providers dataset.

    Args:
        output_path (str, optional): Path to the output directory. Defaults to ".".
    """
    
    prov_data = get_prov_data()
    output_path = output_path.rstrip("/")
    prov_data.serialize(format="trig", destination = f"{output_path}/care-providers-prov.trig")


if __name__ == "__main__":
    create_prov_data()
