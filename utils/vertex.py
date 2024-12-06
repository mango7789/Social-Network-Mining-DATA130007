import os
import pickle
from typing import List


class Vertex:
    def __init__(
        self,
        title: str,
        authors: List[str],
        year: int,
        venue: str,
        index: str,
        references: List[str],
    ):
        self.id = index
        self.title = title
        self.authors = authors
        self.year = year
        self.venue = venue
        self.references = references

    def __repr__(self):
        return f"Vertex(id={self.id}, title={self.title}, authors={self.authors}, year={self.year}, venue={self.venue}, references={self.references})"

    def dump(self, pkl_dir: str):
        pkl_path = pkl_dir + os.sep + self.id + ".pkl"
        with open(pkl_path, "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def load(pkl_path: str):
        with open(pkl_path, "rb") as file:
            vertex = pickle.load(file)
        return vertex


class Edge:
    def __init__(self):
        pass


if __name__ == "__main__":
    vertex = Vertex(
        title="Understanding Serialization",
        authors=["Alice", "Bob"],
        year=2023,
        venue="Tech Journal",
        index="12345",
        references=["54321", "67890"],
    )

    pkl_dir = os.path.join("data", "vertex")
    os.makedirs(pkl_dir, exist_ok=True)

    # Serialize the Vertex object to a file
    vertex.dump(pkl_dir)
    print("Vertex object serialized to 'vertex.pkl'!")

    # Deserialize the Vertex object from the file
    with open(pkl_dir + ".pkl", "rb") as file:
        loaded_vertex = pickle.load(file)
        print(type(loaded_vertex))

    print("Deserialized Vertex object:", loaded_vertex)
