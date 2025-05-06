package edu.kit.datamanager.apeHeplugin;

import edu.kit.datamanager.mappingservice.plugins.*;
import edu.kit.datamanager.mappingservice.util.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.MimeType;
import org.springframework.util.MimeTypeUtils;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.nio.file.Path;
import java.util.Properties;

public class ApeHePlugin implements IMappingPlugin{

    private static String version;

    private final Logger LOGGER = LoggerFactory.getLogger(ApeHePlugin.class);
    private final String REPOSITORY = "https://github.com/kit-data-manager/ape_he_mapper";
    private String TAG;
    private Path dir;

    //private String pluginVenv = "venv/PluginVenv";
    //private String venvInterpreter;

    public ApeHePlugin() {
        try {
            // Get the context class loader
            ClassLoader classLoader = this.getClass().getClassLoader();
            // TODO: do we need to make sure that the resource path is somehow related to the current plugin to avoid loading the wrong property file in case of identical property names?
            URL resource = classLoader.getResource("apeHepluginversion.properties");
            LOGGER.info("Resource file: {}", resource);
            if (resource != null) {
                // Load the properties file
                try (InputStream input = resource.openStream()) {
                    Properties properties = new Properties();
                    properties.load(input);
                    version = properties.getProperty("version");
                    TAG = version;
                }
            } else {
                System.err.println("Properties file not found!");
                version = "unavailable";
                TAG = "unavailable";
            }

            //if (System.getProperty("os.name").startsWith("Windows")) {
            //    venvInterpreter = pluginVenv + "/Scripts/python.exe";
            //} else {
            //    venvInterpreter = pluginVenv + "/bin/python3";
            //}

        } catch (IOException e) {
            e.printStackTrace();
        }
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
    public String version() {
        return version;
    }

    @Override
    public String uri() {
        return REPOSITORY;
    }

    @Override
    public MimeType[] inputTypes() {
        return new MimeType[]{
            MimeTypeUtils.parseMimeType("application/octet-stream"), 
            MimeTypeUtils.parseMimeType("application/x-hdf5"),
            MimeTypeUtils.parseMimeType("application/zip")
        };
    }

    @Override
    public MimeType[] outputTypes() {
        return new MimeType[]{
            MimeTypeUtils.APPLICATION_JSON, 
            MimeTypeUtils.parseMimeType("application/zip")
        };
    }

    @Override
    public void setup() {
        LOGGER.info("Checking and installing dependencies for the tool: ");
        //TODO: test for minimal python version?
        try {
            LOGGER.info("Cloning git repository {}, Tag {}", REPOSITORY, TAG);
            dir = FileUtil.cloneGitRepository(REPOSITORY, TAG);
            // Install Python dependencies

            ProcessBuilder pb = new ProcessBuilder("python3", "-m", "pip", "install", "-r", dir + "/requirements.dist.txt");
            pb.inheritIO();
            Process p = pb.start();

            int exitCode = p.waitFor();
            if (exitCode != 0) {
                LOGGER.error("Failed to install Python packages");
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    /* public void setup() {
        LOGGER.trace("Setting up mapping plugin {} {}", name(), version());
        //TODO: test for minimal python version?
        try {
            LOGGER.info("Cloning git repository {}, Tag {}", REPOSITORY, TAG);
            dir = FileUtil.cloneGitRepository(REPOSITORY, TAG);
            // Install Python dependencies

            MappingPluginState venvState = PythonRunnerUtil.runPythonScript("-m", "venv", "--system-site-packages", dir + "/" + pluginVenv);
            if (MappingPluginState.SUCCESS().getState().equals(venvState.getState())) {
                LOGGER.info("Venv for plugin installed successfully.");
                LOGGER.info("Installing packages");
                ShellRunnerUtil.run(dir + "/" + venvInterpreter, "-m", "pip", "install", "-r", dir + "/" + "requirements.dist.txt");
            } else {
                LOGGER.error("venv installation was not successful");
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    } */

    @Override
    public MappingPluginState mapFile(Path mappingFile, Path inputFile, Path outputFile) throws MappingPluginException {
        long startTime = System.currentTimeMillis();
        LOGGER.trace("Run ApeHe-Mapping-Tool on '{}' with mapping '{}' -> '{}'", mappingFile, inputFile, outputFile);
        //MappingPluginState result = ShellRunnerUtil.run(dir + "/" + venvInterpreter, dir + "/plugin_wrapper.py", "-m", mappingFile.toString(), "-i", inputFile.toString(), "-o", outputFile.toString());
        String[] args = {"-m", mappingFile.toString(), "-i", inputFile.toString(), "-o", outputFile.toString()};
        MappingPluginState result = PythonRunnerUtil.runPythonScript(dir + "/plugin_wrapper.py", args);
        long endTime = System.currentTimeMillis();
        long totalTime = endTime - startTime;
        LOGGER.info("Execution time of mapFile: {} milliseconds", totalTime);
        return result;
    }
}
