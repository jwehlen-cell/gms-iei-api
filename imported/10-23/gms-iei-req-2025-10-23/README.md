# gms-iei-req (comment)



## GMS IEI Requirements

This respository contains the IntelliEarth Integrator (IEI) endpoint requirements in the form of architectural documents, OpenAPI specifications, and
test criteria.  

In general, the endpoint requirments are organized by `"domain"` (Interval, Station, Waveform, Signal Detection, and Event) where each set of requirements
is provided in a "domain directory".  In addition to domain specific artifacts, OpenAPI specifications for objects (in the **Common Object Interface** format 
or **COI**) that are common to more than one domain are provided in the `Common` directory. 

The directory structure providing the requirement artifacts is as follows:
  - **Common/**
        Contains a subdirectory `OpenAPISpec` for COI objects common across domains
  - **\<Domain\>/**  (for example:  `Interval/`)
    - Contains the following sub-directories:
      - **ArchitectureDocs/** - This directory typically contains a single PDF file with supporting architecture information such as 
        background information, GMS/IAN contextual information, COI class diagrams and descriptions, etc. ,
      - **OpenAPISpec/** -  This directory contains `yaml` files with OpenAPI specifications for the COI data model and each required endpoint to be implemented. Multiple files are used to separate the COI data model and endpoint specifications.
      - **TestCriteria**/ - This directory contains files that provide test/validation criteria for each domain endpoint.
