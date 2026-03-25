package edu.kit.datamanager.apeHeplugin;

import edu.kit.datamanager.mappingservice.plugins.AbstractPythonMappingPlugin;
import java.nio.file.Path;

public class ApeHePlugin extends AbstractPythonMappingPlugin{

    private static final String REPOSITORY = "https://github.com/kit-data-manager/ape_he_mapper";


    public ApeHePlugin() {
        super("ApeHe_nxs2JSON", REPOSITORY);
    }

    @Override
    public String name() {
        return "ApeHe_nxs2JSON";
    }

    @Override
    public String description() {
        return "This python based tool extracts metadata from outputs of APE-HE experiment and generates a JSON file adhering to the schema.";
    }

    @Override
    public String[] inputTypes() {
        return new String[]{
            "application/octet-stream", 
            "application/x-hdf5",
            "application/zip"
        };
    }

    @Override
    public String[] outputTypes() {
        return new String[]{
            "application/json", 
            "application/zip"
        };
    }

    @Override
    public String[] getCommandArray(Path workingDir, Path mappingFile, Path inputFile, Path outputFile) {
        return new String[]{
                workingDir + "/plugin_wrapper.py",
                "-m",
                mappingFile.toString(),
                "-i",
                inputFile.toString(),
                "-o",
                outputFile.toString()
        };
    }
}
