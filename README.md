<!--![Tests](https://github.com/kit-data-manager/tomo_mapper/actions/workflows/python-app.yml/badge.svg)-->
<!--![Tests](https://img.shields.io/github/actions/workflow/status/kit-data-manager/tomo_mapper/python-app.yml?label=Tests)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)-->

# APE-HE Beamline Mapper

## Overview
APE-HE Mapper is a tool designed for mapping APE-HE (Advanced Photoelectric Effect - High Energy) metadata to a uniform, schema-compliant json format. This project includes the extraction of metadata from NeXus (.nxs) files and can be extended for other existing formats.

The target format of the mapper follows pre-defined schemas developed for metadata description of APE-HE experiments.

## About APE-HE
APE-HE is a beamline at the Elettra-Sincrotrone Trieste synchrotron, where a range of scientific techniques are performed. The current implementation supports techniques listed in the NeXus schema: `XAS`, `XMCD`, `IV CURVE`, `2D MAP`, which represent the subset of experiments that have been made FAIR-compliant so far.

## Usage

### 1. Python Command Line Interface

#### Prerequisites

Minimal supported python version: 3.10

#### Cloning the Repository
To get started, clone the repository and navigate to the project directory:
```
git clone https://github.com/kit-data-manager/ape_he_mapper.git
cd ape_he_mapper
```

#### Setting Up the Environment
You can optionally set up a virtual environment. Depending on your environment, you may have to use the `python3` alias instead of `python` for the following commands.

Install the required dependencies:
```
pip install -r requirements.txt
```

#### Running the Mapper
To run the mapper, use the `mapping_cli` module:
```
python -m mapping_cli
```

**1. For single file**

The mapper expects a map file, a metadata file, and a JSON output path:
```
python -m mapping_cli <path_to_schema.json> <path_to_NeXus_file.nxs> <output_document.json>
```

For further information about the necessary map file, see [Mapping README](./src/resources/maps/mapping)

**2. For zipped files** (Under development)

The mapper expects a map file, a zip file, and a zip output path:
```
python -m mapping_cli <path_to_schema.json> <path_to_zipped_NeXus_files.zip> <output_document.zip>
```

For further information about the necessary map file, see [Parsing README](./src/resources/maps/parsing)

For further information about mappings used internally, see [Mapping README](./src/resources/maps/mapping)

### 2. Command Line Interface Executable

Each release contains the python CLI as platform-specific packaged executable. Usage is identical to use with python, just replace
`python -m mapping_cli` with the platform-specific executable.

### 3. Usage as plugin for the [Mapping-Service](https://github.com/kit-data-manager/mapping-service)

The mapper can be used as a plugin for the [kit-data-manager/Mapping-Service](https://github.com/kit-data-manager/mapping-service). The necessary gradle project to build the plugin is included in the [plugin subfolder](./mappingservice-plugin).

Plugin and Python code base share the same semantic versioning, so the plugin version always indicates the specific script version used for mapping. This behaviour can be explicitly overriding 
(for example for testing or for working with older versions of the mapping service). To do this, on gradle build time provide the environment variable `VERSION_OVERRIDE_BY_BRANCH`.
The variable needs to contain a branch name of this repo and branch deletion may break a plugin in use. Only use this option very carefully. Do not use this option for production. 

## Testing
Run tests using `pytest`:
```
pytest
```

## Supported instruments and formats

The following list provides the range of formats, that have been tested via sample data.

### NeXus Metadata File

- neXus

## Acknowlegdements

