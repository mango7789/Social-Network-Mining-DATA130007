import os
import json
import ijson
import multiprocessing
from tqdm import tqdm

# Specify input and output file paths
input_file_path = "../data/dblp_v14.json"
output_file_path_template_nr = "../data/small/dblp_v14_{}.json"
output_file_path_template_wr = "../data/large/dblp_v14_{}.json"

# List of fields to extract
fields_to_extract_nr = [
    "id",
    "title",
    "authors",
    "venue",
    "year",
    "keywords",
    "references",
    "n_citation",
    "doc_type",
    "lang",
]

fields_to_extract_wr = [
    "id",
    "title",
    "authors",
    "venue",
    "year",
    "keywords",
    "fos",
    "references",
    "n_citation",
    "doc_type",
    "lang",
]

# Total number of papers
total_records = 5_259_858
# The number of papers per chunk
records_per_chunk = 99_999


# Function to process and save each chunk in a separate process
def process_chunk(chunk_count, chunk_records, print_lock, output_file_path_template):
    output_file_path = output_file_path_template.format(chunk_count)
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        json.dump(chunk_records, output_file, indent=2)

    with print_lock:
        print(f"\nChunk {chunk_count} saved to {output_file_path}")


def process_json_file(reserve):
    """Process the file and split the records into chunks"""
    with open(input_file_path, "r", encoding="utf-8") as input_file:
        chunk_count = 1
        record_count = 0
        chunk_records = []

        # Create a pool of worker processes
        with multiprocessing.Pool() as pool:
            # Use multiprocessing Manager for thread-safe printing
            manager = multiprocessing.Manager()
            print_lock = manager.Lock()

            if reserve in ["Y", "y"]:
                fields_to_extract = fields_to_extract_wr
                output_file_path_template = output_file_path_template_wr
                os.makedirs("../data/large", exist_ok=True)
            elif reserve in ['N', 'n']:
                fields_to_extract = fields_to_extract_nr
                output_file_path_template = output_file_path_template_nr
                os.makedirs("../data/small", exist_ok=True)
            else:
                raise ValueError("Please input y or n!")

            # Iterate through the JSON file and extract desired fields
            for record in tqdm(ijson.items(input_file, "item"), total=total_records):
                # Extract the fields we need
                filtered_record = {
                    field: record[field]
                    for field in fields_to_extract
                    if field in record
                }

                # Skip the data with missing values
                if len(filtered_record) != len(fields_to_extract):
                    continue

                # Convert the Decimal to float
                if "fos" in record:
                    for item in record["fos"]:
                        item["w"] = float(item["w"])

                chunk_records.append(filtered_record)
                record_count += 1

                # If we reach the number of records per chunk, save the chunk asynchronously
                if record_count >= records_per_chunk:
                    # Submit the current chunk for asynchronous processing
                    pool.apply_async(
                        process_chunk,
                        args=(
                            chunk_count,
                            chunk_records,
                            print_lock,
                            output_file_path_template,
                        ),
                    )

                    # Reset for the next chunk
                    chunk_records = []
                    record_count = 0
                    chunk_count += 1

            # Save any remaining records in the final chunk
            if chunk_records:
                pool.apply_async(
                    process_chunk,
                    args=(
                        chunk_count,
                        chunk_records,
                        print_lock,
                        output_file_path_template,
                    ),
                )

            # Close the pool and wait for all worker processes to complete
            pool.close()
            pool.join()


if __name__ == "__main__":
    reserve = input("Should I reserve the information of fos? [y or n] ")
    process_json_file(reserve)
