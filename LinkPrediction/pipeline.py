import random
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from .model import RandomForest
from .feature import extract_author_features

from utils.logger import logger


def prepare_data_for_training(nodes_df, edges_df):
    """
    Prepare the training data by extracting features for both positive and negative samples.

    Parameters:
    - nodes_df: DataFrame containing paper information (with authors, year, venue, and start/end).
    - edges_df: DataFrame containing edge information between authors (src, dst).

    Returns:
    - X: DataFrame of feature vectors for training.
    - y: Series of labels (1 for positive samples, 0 for negative samples).
    """
    features = []
    labels = []

    # Extract features for positive samples (existing edges between authors)
    for idx, edge in edges_df.iterrows():
        src_author = edge["src"]
        dst_author = edge["dst"]
        feature_vector = extract_author_features(
            src_author, dst_author, nodes_df, edges_df
        )
        features.append(feature_vector)
        labels.append(1)  # Positive sample (existing link)

    # Negative sampling: Create random pairs of authors who have not collaborated
    all_authors = list(
        set(author for authors_list in nodes_df["authors"] for author in authors_list)
    )

    # Add the same number of negative samples as positive samples
    for _ in range(len(labels)):
        random_pair = random.sample(all_authors, 2)  # Pick two random authors
        feature_vector = extract_author_features(
            int(random_pair[0]), int(random_pair[1]), nodes_df, edges_df
        )
        features.append(feature_vector)
        labels.append(0)  # Negative sample (no existing link)

    # Convert features to a DataFrame
    X = pd.DataFrame(
        features,
        columns=[
            "coauthorship_count",
            "jaccard_index",
            "same_year",
            "same_venue",
            "common_coauthors",
        ],
    )
    y = pd.Series(labels)

    return X, y


def train_link_prediction_model(X, y):
    """
    Train a model for link prediction using the provided features and labels.

    Parameters:
    - X: DataFrame of feature vectors.
    - y: Series of labels (1 for positive samples, 0 for negative samples).

    Returns:
    - clf: Trained model.
    """
    # Split data into training and testing sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Initialize the model
    clf = RandomForest()

    # Train the model on the training data
    clf.fit(X_train, y_train)

    # Evaluate the model's performance on the test set
    y_pred = clf.predict(X_test)

    # Log evaluation metrics
    logger.info(f"Accuracy: {accuracy_score(y_test, y_pred)}")
    logger.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")

    return clf


def predict_link(clf, author1, author2, nodes_df, edges_df):
    """
    Predict whether two authors will collaborate in the future based on their features.

    Parameters:
    - clf: Trained model.
    - author1: The first author.
    - author2: The second author.
    - nodes_df: DataFrame containing paper information (with authors, year, venue, and start/end).
    - edges_df: DataFrame containing edge information between authors (src, dst).

    Returns:
    - Prediction: 1 if the authors will likely collaborate, 0 otherwise.
    """
    # Extract features for this author pair
    feature_vector = extract_author_features(author1, author2, nodes_df, edges_df)
    new_data = pd.DataFrame(
        [feature_vector],
        columns=[
            "coauthorship_count",
            "jaccard_index",
            "same_year",
            "same_venue",
            "common_coauthors",
        ],
    )

    # Predict if they will collaborate
    prediction = clf.predict(new_data)

    if prediction == 1:
        logger.info(
            f"Prediction: Authors {author1} and {author2} are likely to collaborate."
        )
    else:
        logger.info(
            f"Prediction: Authors {author1} and {author2} are unlikely to collaborate."
        )

    return prediction


if __name__ == "__main__":
    """
    The process of the link prediction is:
    - Extract existing edges from `author/edge.csv`
    - Use the info in `author/node.csv` to extract the papers `src` and `dst` co-authored, get the feature of year, venue. (We should cope with the problem of co-authors are already in the same year and venue)
    - Calculate the Jaccard/Dice/Cosine index, number of common co-authors.
    - Generate negative examples, label it as 0.
    - Train a classification model using these features.
    - Predict link using this model. Evaluate on time series.
    """
    from utils import load_paper_node, load_paper_edge

    nodes_df = load_paper_node("test/paper/node.csv")
    edges_df = load_paper_edge("test/author/edge.csv")

    X, y = prepare_data_for_training(nodes_df, edges_df)

    clf = train_link_prediction_model(X, y)

    author1 = 1
    author2 = 2
    predict_link(clf, author1, author2, nodes_df, edges_df)
