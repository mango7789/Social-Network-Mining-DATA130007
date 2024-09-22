import ijson
import json
import math
from tqdm import tqdm

# Specify input and output file paths
input_file_path = "../data/dblp_v14.json"
output_file_path_template = "../data/dblp_v14_{}.json"

# List of fields to extract
fields_to_extract = [
    "id",
    "title",
    "authors",
    "venue",
    "year",
    "references",
    "n_citation",
    "doc_type",
    "lang",
]

# T5otal number of records by reading them all once
total_records = 5_259_858
# Calculate the number of records per chunk
records_per_chunk = math.ceil(total_records / 20)


# Now, process the file and split the records into 20 chunks
with open(input_file_path, "r", encoding="utf-8") as input_file:
    chunk_count = 1
    record_count = 0
    chunk_records = []

    # Iterate through the JSON file and extract desired fields
    for record in tqdm(ijson.items(input_file, "item")):
        # Extract the fields we need
        filtered_record = {
            field: record[field] for field in fields_to_extract if field in record
        }
        chunk_records.append(filtered_record)
        record_count += 1

        # If we reach the number of records per chunk, save the chunk and start a new one
        if record_count >= records_per_chunk:
            # Save the current chunk to a file
            output_file_path = output_file_path_template.format(chunk_count)
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                json.dump(chunk_records, output_file, indent=2)

            print(f"\nChunk {chunk_count} saved to {output_file_path}")
            # Reset for the next chunk
            chunk_records = []
            record_count = 0
            chunk_count += 1

    # Save any remaining records in the final chunk
    if chunk_records:
        output_file_path = output_file_path_template.format(chunk_count)
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            json.dump(chunk_records, output_file, indent=2)
        print(f"Chunk {chunk_count} saved to {output_file_path}")