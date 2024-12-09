import math
import json
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from typing import Final, List


def group_records(lines: List[str]) -> List[List[str]]:
    """
    Groups lines into records, ensuring each group corresponds to a complete Vertex object.
    """
    records = []
    current_record = []

    for line in tqdm(lines, desc="Grouping records...  "):
        if line.strip() == "":
            continue
        if line.startswith("#*") and current_record:
            # Start of a new record, save the current one
            records.append(current_record)
            current_record = []
        current_record.append(line)

    # Add the last record
    if current_record:
        records.append(current_record)

    return records


def process_records_to_dataframe(records: List[List[str]]) -> pd.DataFrame:
    """
    Process records to extract Vertex objects and convert them to a DataFrame.
    """
    data = []
    with tqdm(total=len(records), desc="Processing records...") as pbar:
        for record in records:
            vertex_dict = {}
            for line in record:
                line = line.strip()
                if line.startswith("#*"):
                    vertex_dict["title"] = line[2:]
                elif line.startswith("#@"):
                    vertex_dict["authors"] = line[2:]
                elif line.startswith("#t"):
                    vertex_dict["year"] = int(line[2:]) if line[2:] else ""
                elif line.startswith("#c"):
                    vertex_dict["venue"] = line[2:]
                elif line.startswith("#index"):
                    vertex_dict["index"] = line[6:]
                elif line.startswith("#%"):
                    if "references" not in vertex_dict:
                        vertex_dict["references"] = []
                    vertex_dict["references"].append(line[2:])

            # Handle missing fields
            for str_name in ["title", "year", "venue", "authors"]:
                if str_name not in vertex_dict:
                    vertex_dict[str_name] = ""
            for lst_name in ["references"]:
                if lst_name not in vertex_dict:
                    vertex_dict[lst_name] = []

            # Append to data
            data.append(
                {
                    "id": vertex_dict["index"],
                    "title": vertex_dict["title"],
                    "authors": vertex_dict["authors"].replace(", ", "#"),
                    "year": vertex_dict["year"],
                    "venue": vertex_dict["venue"],
                    "references": "#".join(vertex_dict["references"]),
                }
            )

            pbar.update(1)

    return pd.DataFrame(data)


def load_save_vertex_to_csv(
    data_path: str,
    output_dir: str,
    config_path: str,
    chunk_size_limit: int = 500000,
) -> int:
    """
    Load and preprocess the dataset, and save as CSV in a single process.
    Additionally, save the start and end IDs of each chunk in a JSON file.
    """
    # Read the entire dataset
    with open(data_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Group lines into records
    records = group_records(lines)

    # Process all records into a single DataFrame
    combined_data = process_records_to_dataframe(records)

    # Save the DataFrame to CSV files in chunks
    output_dir.mkdir(parents=True, exist_ok=True)

    chunk_info = {}
    num_chunks = math.ceil(len(combined_data) / chunk_size_limit)

    for i in range(num_chunks):
        start = i * chunk_size_limit
        end = (i + 1) * chunk_size_limit
        chunk = combined_data.iloc[start:end]
        chunk_file = output_dir / f"chunk_{i + 1}.csv"
        chunk.to_csv(chunk_file, index=False, encoding="utf-8")

        # Record first and last IDs in the chunk
        chunk_info[str(chunk_file)] = {
            "first_id": chunk.iloc[0]["id"] if not chunk.empty else None,
            "last_id": chunk.iloc[-1]["id"] if not chunk.empty else None,
        }

        print(f"Saved {chunk_file} with {len(chunk)} vertices.")

    # Save chunk info to JSON
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(chunk_info, f, indent=4)

    return len(combined_data)
