from sklearn.ensemble import RandomForestClassifier


def RandomForest():
    model = RandomForestClassifier(n_estimators=100, random_state=42, verbose=1)
    return model
