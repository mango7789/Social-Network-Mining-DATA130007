import org.neo4j.driver.TransactionWork;

import java.util.List;
import java.util.Map;

public class Neo4jImporter {

    public void importDataset(Neo4jConnection connection, List<Map<String, Object>> dataset) {
        for (Map<String, Object> record : dataset) {
            String paperId = (String) record.get("id");
            String title = (String) record.get("title");
            String venue = (String) ((Map<String, Object>) record.get("venue")).get("raw");
            int year = (int) record.get("year");
            int nCitation = (int) record.get("n_citation");
            String docType = (String) record.get("doc_type");

            // Create or merge Paper node
            connection.getSession().writeTransaction((TransactionWork<Void>) tx -> {
                tx.run("MERGE (p:Paper {id: $id}) " +
                        "SET p.title = $title, p.year = $year, p.venue = $venue, " +
                        "p.n_citation = $nCitation, p.doc_type = $docType",
                        Map.of("id", paperId, "title", title, "year", year,
                                "venue", venue, "nCitation", nCitation, "docType", docType));

                // Create Author nodes and relationships
                List<Map<String, String>> authors = (List<Map<String, String>>) record.get("authors");
                for (Map<String, String> author : authors) {
                    String authorId = author.get("id");
                    String authorName = author.get("name");
                    String authorOrg = author.get("org");

                    // Create or merge Author node
                    tx.run("MERGE (a:Author {id: $authorId}) " +
                            "SET a.name = $authorName, a.org = $authorOrg",
                            Map.of("authorId", authorId, "authorName", authorName, "authorOrg", authorOrg));

                    // Create AUTHORED_BY relationship
                    tx.run("MATCH (p:Paper {id: $paperId}), (a:Author {id: $authorId}) " +
                            "MERGE (a)-[:AUTHORED_BY]->(p)",
                            Map.of("paperId", paperId, "authorId", authorId));
                }

                // Create CITED relationships if there are references
                List<String> references = (List<String>) record.get("references");
                for (String referenceId : references) {
                    // Create or merge referenced Paper node if necessary
                    tx.run("MERGE (ref:Paper {id: $referenceId}) " +
                            "MERGE (p:Paper {id: $paperId}) " +
                            "MERGE (p)-[:CITED]->(ref)",
                            Map.of("referenceId", referenceId, "paperId", paperId));
                }

                return null;
            });
        }
    }
}
