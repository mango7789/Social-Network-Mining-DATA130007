import os
import pickle
from tqdm import tqdm
from typing import Final, List
from concurrent.futures import ProcessPoolExecutor
from vertex import Vertex

DATA_PATH: Final = os.path.join("data", "dblp.v9", "dblp.txt")
PKL_DIR: Final = os.path.join("data", "vertices")
os.makedirs(PKL_DIR, exist_ok=True)


def group_records(lines: List[str]) -> List[List[str]]:
    """
    Groups lines into records, ensuring each group corresponds to a complete Vertex object.
    Args:
        lines (List[str]): The lines of the dataset.
    Returns:
        List[List[str]]: A list of grouped lines, each group representing a complete Vertex record.
    """
    records = []
    current_record = []

    for line in lines:
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


def process_chunk_with_progress(
    records: List[List[str]], pkl_dir: str, worker_id: int
) -> int:
    """
    Process a chunk of records to extract and save Vertex objects, showing progress for this worker.
    Args:
        records (List[List[str]]): List of grouped lines in the chunk.
        pkl_dir (str): Directory to save the serialized Vertex objects.
        worker_id (int): Worker ID for identifying the progress bar.
    Returns:
        int: Number of Vertex objects processed in the chunk.
    """
    count = 0

    with tqdm(
        total=len(records), desc=f"Worker {worker_id}", position=worker_id
    ) as pbar:
        for record in records:
            vertex_dict = {}
            for line in record:
                line = line.strip()
                if line.startswith("#*"):
                    vertex_dict["title"] = line[2:]
                elif line.startswith("#@"):
                    vertex_dict["authors"] = line[2:]
                elif line.startswith("#t"):
                    vertex_dict["year"] = int(line[2:])
                elif line.startswith("#c"):
                    vertex_dict["venue"] = line[2:]
                elif line.startswith("#index"):
                    vertex_dict["index"] = line[6:]
                elif line.startswith("#%"):
                    if "references" not in vertex_dict:
                        vertex_dict["references"] = []
                    vertex_dict["references"].append(line[2:])

            # Handle missing fields
            for str_name in ["title", "year", "venue"]:
                if str_name not in vertex_dict:
                    vertex_dict[str_name] = None
            for lst_name in ["authors", "references"]:
                if lst_name not in vertex_dict:
                    vertex_dict[lst_name] = []

            # Serialize the Vertex object
            curr_vertex = Vertex(**vertex_dict)
            with open(os.path.join(pkl_dir, f"{curr_vertex.id}.pkl"), "wb") as pkl_file:
                pickle.dump(curr_vertex, pkl_file)

            count += 1
            pbar.update(1)  # Update progress bar

    return count


def load_save_vertex_parallel(data_path: str, pkl_dir: str, num_workers: int = 4):
    """
    Load and preprocess the dataset in parallel with grouped records.
    Args:
        data_path (str): Path to the dataset.
        pkl_dir (str): Directory to save the serialized Vertex objects.
        num_workers (int): Number of parallel workers.
    """
    # Read the entire dataset
    with open(data_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Group lines into records
    records = group_records(lines)

    # Split records into chunks for parallel processing
    chunk_size = len(records) // num_workers
    chunks = [records[i : i + chunk_size] for i in range(0, len(records), chunk_size)]

    total_vertices = 0
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Map chunks to workers with individual progress bars
        results = list(
            executor.map(
                process_chunk_with_progress,
                chunks,
                [pkl_dir] * len(chunks),
                range(len(chunks)),  # Worker IDs
            )
        )

    total_vertices = sum(results)
    print(f"There are total {total_vertices} vertices in the dataset!")


if __name__ == "__main__":
    load_save_vertex_parallel(DATA_PATH, PKL_DIR, num_workers=4)
