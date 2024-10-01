import java.util.List;
import java.util.Map;

public class Main {
    public static void main(String[] args) {
        
        List<Map<String, Object>> dataset = List.of();

        Neo4jConnection connection = new Neo4jConnection();
        Neo4jImporter importer = new Neo4jImporter();

        importer.importDataset(connection, dataset);
        connection.close();
    }
}
