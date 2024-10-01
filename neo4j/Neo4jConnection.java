import org.neo4j.driver.AuthTokens;
import org.neo4j.driver.GraphDatabase;
import org.neo4j.driver.Session;

public class Neo4jConnection {
    private final String uri = "bolt://localhost:7687"; // Change to your Neo4j instance
    private final String user = "neo4j"; // Your Neo4j username
    private final String password = "password"; // Your Neo4j password
    private final Session session;

    public Neo4jConnection() {
        var driver = GraphDatabase.driver(uri, AuthTokens.basic(user, password));
        session = driver.session();
    }

    public Session getSession() {
        return session;
    }

    public void close() {
        session.close();
    }
}
