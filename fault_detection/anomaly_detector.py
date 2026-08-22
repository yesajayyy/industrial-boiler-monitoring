import os

import joblib
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


class BoilerAnomalyDetector:
    """
    Hybrid anomaly detection system for an industrial boiler.

    Isolation Forest provides machine-learning based anomaly
    detection.

    Process limit checks identify known abnormal operating
    conditions and provide interpretable fault indicators.

    The SafetySystem remains responsible for the actual
    emergency shutdown and safety interlock.
    """

    FEATURES = [
        "temperature",
        "pressure",
        "level",
        "flow",
    ]

    MAX_TEMPERATURE = 210.0
    MAX_PRESSURE = 10.0
    MIN_LEVEL = 20.0
    MIN_FLOW = 10.0

    def __init__(
        self,
        model_path="models/boiler_anomaly_model.pkl",
    ):
        self.model_path = model_path
        self.model = None

    def train(
        self,
        csv_path="data/boiler_training_dataset.csv",
        contamination=0.05,
        random_state=42,
    ):
        """
        Train Isolation Forest using only normal process data.
        """

        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"Dataset not found: {csv_path}"
            )

        data = pd.read_csv(csv_path)

        required_columns = self.FEATURES + ["fault_type"]

        missing_columns = [
            column
            for column in required_columns
            if column not in data.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        normal_data = data[
            data["fault_type"] == "NORMAL"
        ].copy()

        if len(normal_data) < 100:
            raise ValueError(
                "Not enough normal samples for training."
            )

        training_features = normal_data[
            self.FEATURES
        ].astype(float)

        self.model = IsolationForest(
            n_estimators=300,
            contamination=contamination,
            random_state=random_state,
        )

        self.model.fit(training_features)

        model_directory = os.path.dirname(
            self.model_path
        )

        if model_directory:
            os.makedirs(
                model_directory,
                exist_ok=True,
            )

        joblib.dump(
            self.model,
            self.model_path,
        )

        return {
            "training_samples": len(training_features),
            "total_samples": len(data),
            "model_path": self.model_path,
        }

    def load(self):
        """
        Load a previously trained Isolation Forest model.
        """

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model not found: {self.model_path}"
            )

        self.model = joblib.load(
            self.model_path
        )

        return self.model

    def detect_faults(self, sensor_data):
        """
        Identify known process faults from sensor limits.
        """

        temperature = float(
            sensor_data["temperature"]
        )

        pressure = float(
            sensor_data["pressure"]
        )

        level = float(
            sensor_data["level"]
        )

        flow = float(
            sensor_data["flow"]
        )

        faults = []

        if temperature >= self.MAX_TEMPERATURE:
            faults.append(
                "HIGH TEMPERATURE"
            )

        if pressure >= self.MAX_PRESSURE:
            faults.append(
                "HIGH PRESSURE"
            )

        if level <= self.MIN_LEVEL:
            faults.append(
                "LOW WATER LEVEL"
            )

        if flow <= self.MIN_FLOW:
            faults.append(
                "LOW FLOW"
            )

        return faults

    def predict(self, sensor_data):
        """
        Analyze one process state.

        Returns the machine-learning result together with
        interpretable process fault indicators.
        """

        if self.model is None:
            if os.path.exists(self.model_path):
                self.load()
            else:
                raise RuntimeError(
                    "Model is not trained."
                )

        values = pd.DataFrame(
            [
                [
                    sensor_data["temperature"],
                    sensor_data["pressure"],
                    sensor_data["level"],
                    sensor_data["flow"],
                ]
            ],
            columns=self.FEATURES,
        )

        ml_prediction = self.model.predict(
            values
        )[0]

        anomaly_score = self.model.decision_function(
            values
        )[0]

        ml_anomaly = (
            ml_prediction == -1
        )

        process_faults = self.detect_faults(
            sensor_data
        )

        if ml_anomaly or process_faults:
            status = "ANOMALY"
        else:
            status = "NORMAL"

        return {
            "status": status,
            "ml_prediction": int(
                ml_prediction
            ),
            "ml_anomaly": ml_anomaly,
            "anomaly_score": round(
                float(anomaly_score),
                4,
            ),
            "faults": process_faults,
        }

    def evaluate(
        self,
        csv_path="data/boiler_training_dataset.csv",
    ):
        """
        Evaluate the Isolation Forest against the labeled
        dataset.
        """

        if self.model is None:
            if os.path.exists(self.model_path):
                self.load()
            else:
                raise RuntimeError(
                    "Model is not trained."
                )

        data = pd.read_csv(csv_path)

        features = data[
            self.FEATURES
        ].astype(float)

        actual = (
            data["fault_type"] != "NORMAL"
        ).astype(int)

        predictions = self.model.predict(
            features
        )

        predicted = (
            predictions == -1
        ).astype(int)

        accuracy = accuracy_score(
            actual,
            predicted,
        )

        precision = precision_score(
            actual,
            predicted,
            zero_division=0,
        )

        recall = recall_score(
            actual,
            predicted,
            zero_division=0,
        )

        f1 = f1_score(
            actual,
            predicted,
            zero_division=0,
        )

        matrix = confusion_matrix(
            actual,
            predicted,
        )

        report = classification_report(
            actual,
            predicted,
            target_names=[
                "NORMAL",
                "FAULT",
            ],
            zero_division=0,
        )

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "confusion_matrix": matrix,
            "classification_report": report,
        }


def main():
    detector = BoilerAnomalyDetector()

    print("=" * 70)
    print("INDUSTRIAL BOILER ML ANOMALY DETECTOR")
    print("=" * 70)

    print()
    print("Training model...")

    training_result = detector.train()

    print()
    print(
        f"Training samples: "
        f"{training_result['training_samples']}"
    )

    print(
        f"Total dataset samples: "
        f"{training_result['total_samples']}"
    )

    print(
        f"Model saved to: "
        f"{training_result['model_path']}"
    )

    print()
    print("Evaluating Isolation Forest...")

    evaluation = detector.evaluate()

    print()
    print(
        f"Accuracy:  "
        f"{evaluation['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{evaluation['precision']:.4f}"
    )

    print(
        f"Recall:    "
        f"{evaluation['recall']:.4f}"
    )

    print(
        f"F1 Score:  "
        f"{evaluation['f1_score']:.4f}"
    )

    print()
    print("Confusion Matrix:")
    print(
        evaluation["confusion_matrix"]
    )

    print()
    print("Classification Report:")
    print(
        evaluation["classification_report"]
    )

    print("=" * 70)

    print()
    print("Testing individual process conditions...")
    print()

    test_conditions = {
        "NORMAL CONDITION": {
            "temperature": 165.0,
            "pressure": 6.0,
            "level": 65.0,
            "flow": 38.0,
        },
        "HIGH PRESSURE": {
            "temperature": 165.0,
            "pressure": 11.0,
            "level": 65.0,
            "flow": 38.0,
        },
        "HIGH TEMPERATURE": {
            "temperature": 225.0,
            "pressure": 8.0,
            "level": 65.0,
            "flow": 38.0,
        },
        "LOW LEVEL": {
            "temperature": 165.0,
            "pressure": 6.0,
            "level": 10.0,
            "flow": 38.0,
        },
        "LOW FLOW": {
            "temperature": 165.0,
            "pressure": 6.0,
            "level": 65.0,
            "flow": 7.0,
        },
    }

    for name, condition in test_conditions.items():

        result = detector.predict(
            condition
        )

        print(
            f"{name}: {result['status']}"
        )

        print(
            f"  ML anomaly: "
            f"{result['ml_anomaly']}"
        )

        print(
            f"  Anomaly score: "
            f"{result['anomaly_score']}"
        )

        if result["faults"]:
            print(
                f"  Fault indicators: "
                f"{', '.join(result['faults'])}"
            )
        else:
            print(
                "  Fault indicators: None"
            )

        print()


if __name__ == "__main__":
    main()
