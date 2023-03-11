#!/usr/bin/env python3
from rdflib import Graph


IC1 = """
ASK {
  {
    # Check observation has a data set
    ?obs a qb:Observation .
    FILTER NOT EXISTS { ?obs qb:dataSet ?dataset1 . }
  } UNION {
    # Check has just one data set
    ?obs a qb:Observation ;
       qb:dataSet ?dataset1, ?dataset2 .
    FILTER (?dataset1 != ?dataset2)
  }
}"""
IC2 = """
ASK {
  {
    # Check dataset has a dsd
    ?dataset a qb:DataSet .
    FILTER NOT EXISTS { ?dataset qb:structure ?dsd . }
  } UNION { 
    # Check has just one dsd
    ?dataset a qb:DataSet ;
       qb:structure ?dsd1, ?dsd2 .
    FILTER (?dsd1 != ?dsd2)
  }
}"""
# Modified to include abbreviated "qb:measure" properties (stricter than base implementation)
IC3 = """
ASK {
  ?dsd a qb:DataStructureDefinition .
  FILTER NOT EXISTS { ?dsd qb:component [qb:measure [a qb:MeasureProperty]] }
}"""
IC4 = """
ASK {
  ?dim a qb:DimensionProperty .
  FILTER NOT EXISTS { ?dim rdfs:range [] }
}"""
IC5 = """
ASK {
  ?dim a qb:DimensionProperty ;
       rdfs:range skos:Concept .
  FILTER NOT EXISTS { ?dim qb:codeList [] }
}"""

IC6 = """
ASK {
  ?dsd qb:component ?componentSpec .
  ?componentSpec qb:componentRequired "false"^^xsd:boolean ;
                 qb:componentProperty ?component .
  FILTER NOT EXISTS { ?component a qb:AttributeProperty }
}"""
IC7 = """
ASK {
    ?sliceKey a qb:SliceKey .
    ?dsd a qb:DataStructureDefinition .
    FILTER NOT EXISTS { ?dsd qb:sliceKey ?sliceKey }
}"""
IC8 = """
ASK {
  ?slicekey a qb:SliceKey;
      qb:componentProperty ?prop .
  ?dsd qb:sliceKey ?slicekey .
  FILTER NOT EXISTS { ?dsd qb:component [qb:componentProperty ?prop] }
}"""
IC9 = """
ASK {
  {
    # Slice has a key
    ?slice a qb:Slice .
    FILTER NOT EXISTS { ?slice qb:sliceStructure ?key }
  } UNION {
    # Slice has just one key
    ?slice a qb:Slice ;
           qb:sliceStructure ?key1, ?key2;
    FILTER (?key1 != ?key2)
  }
}"""
IC10 = """
ASK {
  ?slice qb:sliceStructure [qb:componentProperty ?dim] .
  FILTER NOT EXISTS { ?slice ?dim [] }
}"""
IC11 = """
ASK {
    ?obs qb:dataSet/qb:structure/qb:component/qb:componentProperty ?dim .
    ?dim a qb:DimensionProperty;
    FILTER NOT EXISTS { ?obs ?dim [] }
}"""
IC12 = """
ASK {
  FILTER( ?allEqual )
  {
    # For each pair of observations test if all the dimension values are the same
    SELECT (MIN(?equal) AS ?allEqual) WHERE {
        ?obs1 qb:dataSet ?dataset .
        ?obs2 qb:dataSet ?dataset .
        FILTER (?obs1 != ?obs2)
        ?dataset qb:structure/qb:component/qb:componentProperty ?dim .
        ?dim a qb:DimensionProperty .
        ?obs1 ?dim ?value1 .
        ?obs2 ?dim ?value2 .
        BIND( ?value1 = ?value2 AS ?equal)
    } GROUP BY ?obs1 ?obs2
  }
}"""
IC13 = """
ASK {
    ?obs qb:dataSet/qb:structure/qb:component ?component .
    ?component qb:componentRequired "true"^^xsd:boolean ;
               qb:componentProperty ?attr .
    FILTER NOT EXISTS { ?obs ?attr [] }
}"""

IC14 = """
ASK {
    # Observation in a non-measureType cube
    ?obs qb:dataSet/qb:structure ?dsd .
    FILTER NOT EXISTS { ?dsd qb:component/qb:componentProperty qb:measureType }

    # verify every measure is present
    ?dsd qb:component/qb:componentProperty ?measure .
    ?measure a qb:MeasureProperty;
    FILTER NOT EXISTS { ?obs ?measure [] }
}"""
IC15 = """
ASK {
    # Observation in a measureType-cube
    ?obs qb:dataSet/qb:structure ?dsd ;
         qb:measureType ?measure .
    ?dsd qb:component/qb:componentProperty qb:measureType .
    # Must have value for its measureType
    FILTER NOT EXISTS { ?obs ?measure [] }
}"""
IC16 = """
ASK {
    # Observation with measureType
    ?obs qb:dataSet/qb:structure ?dsd ;
         qb:measureType ?measure ;
         ?omeasure [] .
    # Any measure on the observation
    ?dsd qb:component/qb:componentProperty qb:measureType ;
         qb:component/qb:componentProperty ?omeasure .
    ?omeasure a qb:MeasureProperty .
    # Must be the same as the measureType
    FILTER (?omeasure != ?measure)
}"""
IC17 = """
ASK {
  {
      # Count number of other measures found at each point 
      SELECT ?numMeasures (COUNT(?obs2) AS ?count) WHERE {
          {
              # Find the DSDs and check how many measures they have
              SELECT ?dsd (COUNT(?m) AS ?numMeasures) WHERE {
                  ?dsd qb:component/qb:componentProperty ?m.
                  ?m a qb:MeasureProperty .
              } GROUP BY ?dsd
          }
        
          # Observation in measureType cube
          ?obs1 qb:dataSet/qb:structure ?dsd;
                qb:dataSet ?dataset ;
                qb:measureType ?m1 .
    
          # Other observation at same dimension value
          ?obs2 qb:dataSet ?dataset ;
                qb:measureType ?m2 .
          FILTER NOT EXISTS { 
              ?dsd qb:component/qb:componentProperty ?dim .
              FILTER (?dim != qb:measureType)
              ?dim a qb:DimensionProperty .
              ?obs1 ?dim ?v1 . 
              ?obs2 ?dim ?v2. 
              FILTER (?v1 != ?v2)
          }
          
      } GROUP BY ?obs1 ?numMeasures
        HAVING (?count != ?numMeasures)
  }
}"""
IC18 = """
ASK {
    ?dataset qb:slice       ?slice .
    ?slice   qb:observation ?obs .
    FILTER NOT EXISTS { ?obs qb:dataSet ?dataset . }
}"""
# Only checking "skos:ConceptScheme" because skos:Collection is not used at all
IC19 = """
ASK {
    ?obs qb:dataSet/qb:structure/qb:component/qb:componentProperty ?dim .
    ?dim a qb:DimensionProperty ;
        qb:codeList ?list .
    ?list a skos:ConceptScheme .
    ?obs ?dim ?v .
    FILTER NOT EXISTS { ?v a skos:Concept ; skos:inScheme ?list }
}"""
# Not applicable to current data cube
IC20 = """
ASK {
    ?obs qb:dataSet/qb:structure/qb:component/qb:componentProperty ?dim .
    ?dim a qb:DimensionProperty ;
        qb:codeList ?list .
    ?list a qb:HierarchicalCodeList .
    ?obs ?dim ?v .
    FILTER NOT EXISTS { ?list qb:hierarchyRoot ?v }
}"""
# Not applicable to current data cube
IC21 = """
ASK {
    ?obs qb:dataSet/qb:structure/qb:component/qb:componentProperty ?dim .
    ?dim a qb:DimensionProperty ;
         qb:codeList ?list .
    ?list a qb:HierarchicalCodeList .
    ?obs ?dim ?v .
    FILTER NOT EXISTS { ?list qb:hierarchyRoot ?v }
}"""

CONSTRAINTS = [IC1, IC2, IC3, IC4, IC5, IC6, IC7, IC8, IC9, IC10, IC11, IC12, IC13, IC14, IC15, IC16, IC17, IC18, IC19, IC20, IC21]


def validate_dataset(rdf_file_source: str):
    g = Graph()
    g.parse(rdf_file_source)
    print("Validating " + rdf_file_source)
    for i in range(len(CONSTRAINTS)):
        try:
            for row in g.query(CONSTRAINTS[i]):
                print(f"IC{i + 1}: {row}")
        except Exception as ex:
            print(f"IC{i + 1}: {str(ex)}")


def main():
    validate_dataset("care-providers.ttl")
    validate_dataset("population-2021.ttl")


if __name__ == "__main__":
    main()
