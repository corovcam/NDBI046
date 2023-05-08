from population_2021.codelist import create_codelist
from population_2021.data_cube import process_population

from rdflib import Graph, BNode, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD, DCAT, DCTERMS

NS = Namespace("https://ndbi046-martincorovcak.com/ontology#")
NSR = Namespace("https://ndbi046-martincorovcak.com/resources/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
EUROVOC = Namespace("http://eurovoc.europa.eu/")
EUA = Namespace("http://publications.europa.eu/resource/authority/")


def annotate_dataset(g: Graph):
    dataset = NSR["dataset/MeanPopulation2021"]
    
    g.add((dataset, RDF.type, DCAT.Dataset))
    g.add((dataset, DCTERMS.title, Literal("Střední stav obyvatel v Okresech 2021", lang="cs")))
    g.add((dataset, DCTERMS.title, Literal("Mean Population per County 2021", lang="en")))
    g.add((dataset, DCTERMS.description, Literal("Statistika středního stavu obyvatel v okresech a krajích České republiky za rok 2021", lang="cs")))
    g.add((dataset, DCTERMS.description, Literal("Statistics of mean population count per county and region of the Czech Republic for the year 2021", lang="en")))
    g.add((dataset, DCTERMS.publisher, Literal("https://github.com/corovcam", datatype=XSD.anyURI)))
    g.add((dataset, DCTERMS.creator, Literal("https://github.com/corovcam", datatype=XSD.anyURI)))
    g.add((dataset, DCTERMS.issued, Literal("2023-03-11", datatype=XSD.date)))
    g.add((dataset, DCTERMS.modified, Literal("2023-05-08", datatype=XSD.date)))
    
    g.add((dataset, DCAT.keyword, Literal("mean population", lang="en")))
    g.add((dataset, DCAT.keyword, Literal("střední stav obyvatel", lang="cs")))
    g.add((dataset, DCAT.keyword, Literal("population count", lang="en")))
    g.add((dataset, DCAT.keyword, Literal("počet obyvatel", lang="cs")))
    
    g.add((dataset, DCAT.theme, EUROVOC["4259"])) # population statistics
    
    g.add((dataset, DCTERMS.spatial, EUA["country/CZE"])) # Czech Republic
    
    periodOfTime = BNode()
    g.add((dataset, DCTERMS.temporal, periodOfTime))
    g.add((periodOfTime, RDF.type, DCTERMS.PeriodOfTime))
    g.add((periodOfTime, DCAT.startDate, Literal("2021-01-01", datatype=XSD.date)))
    g.add((periodOfTime, DCAT.endDate, Literal("2021-12-31", datatype=XSD.date)))
    
    g.add((dataset, DCTERMS.accrualPeriodicity, EUA["frequency/ANNUAL"]))
    
    g.add((dataset, DCAT.distribution, NSR["dataset/MeanPopulation2021/distribution/rdf-turtle"]))


def create_distribution(g: Graph):
    distribution = NSR["dataset/MeanPopulation2021/distribution/rdf-turtle"]
    
    g.add((distribution, RDF.type, DCAT.Distribution))
    g.add((distribution, DCTERMS.title, Literal("RDF Turtle distribution of Mean Population per County 2021 dataset", lang="en")))
    g.add((distribution, DCTERMS.title, Literal("RDF Turtle distribuce datasetu Střední stav obyvatel v Okresech 2021", lang="cs")))
    g.add((distribution, DCAT.downloadURL, Literal("https://raw.githubusercontent.com/corovcam/ndbi046/main/5-Metadata/population.ttl", datatype=XSD.anyURI)))
    g.add((distribution, DCAT.accessURL, Literal("https://raw.githubusercontent.com/corovcam/ndbi046/main/5-Metadata/population.ttl", datatype=XSD.anyURI)))
    g.add((distribution, DCAT.mediaType, URIRef("https://www.iana.org/assignments/media-types/text/turtle")))
    g.add((distribution, DCTERMS.format, EUA["file-type/RDF_TURTLE"]))


def create_dataset_entry():
    g = Graph(bind_namespaces="rdflib")
    annotate_dataset(g)
    create_distribution(g)
    g.serialize("population-dataset-entry.ttl", format="turtle")


if __name__ == "__main__":
    create_codelist()
    process_population()
    create_dataset_entry()
