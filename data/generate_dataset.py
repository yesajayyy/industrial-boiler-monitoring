import os

import numpy as np
import pandas as pd


RANDOM_SEED = 42
TOTAL_NORMAL_SAMPLES = 5000
FAULT_SAMPLES_PER_TYPE = 500

OUTPUT_FILE = "data/boiler_training_dataset.csv"


def generate_normal_data(count, rng):
    temperature = rng.normal(165, 8, count)
    pressure = rng.normal(6, 0.7, count)
    level = rng.normal(65, 5, count)
    flow = rng.normal(38, 3, count)

    temperature = np.clip(temperature, 140, 185)
    pressure = np.clip(pressure, 4, 8)
    level = np.clip(level, 50, 80)
    flow = np.clip(flow, 28, 48)

    return pd.DataFrame(
        {
            "temperature": temperature,
            "pressure": pressure,
            "level": level,
            "flow": flow,
            "fault_type": "NORMAL",
        }
    )


def generate_high_pressure_data(count, rng):
    temperature = rng.normal(175, 8, count)
    pressure = rng.normal(11.5, 0.8, count)
    level = rng.normal(65, 5, count)
    flow = rng.normal(38, 3, count)

    temperature = np.clip(temperature, 150, 195)
    pressure = np.clip(pressure, 10.5, 14)
    level = np.clip(level, 50, 80)
    flow = np.clip(flow, 25, 50)

    return pd.DataFrame(
        {
            "temperature": temperature,
            "pressure": pressure,
            "level": level,
            "flow": flow,
            "fault_type": "HIGH_PRESSURE",
        }
    )


def generate_high_temperature_data(count, rng):
    temperature = rng.normal(225, 8, count)
    pressure = rng.normal(8, 0.8, count)
    level = rng.normal(65, 5, count)
    flow = rng.normal(38, 3, count)

    temperature = np.clip(temperature, 210, 250)
    pressure = np.clip(pressure, 6, 11)
    level = np.clip(level, 50, 80)
    flow = np.clip(flow, 25, 50)

    return pd.DataFrame(
        {
            "temperature": temperature,
            "pressure": pressure,
            "level": level,
            "flow": flow,
            "fault_type": "HIGH_TEMPERATURE",
        }
    )


def generate_low_level_data(count, rng):
    temperature = rng.normal(165, 8, count)
    pressure = rng.normal(6, 0.7, count)
    level = rng.normal(12, 3, count)
    flow = rng.normal(38, 3, count)

    temperature = np.clip(temperature, 140, 185)
    pressure = np.clip(pressure, 4, 8)
    level = np.clip(level, 2, 18)
    flow = np.clip(flow, 25, 50)

    return pd.DataFrame(
        {
            "temperature": temperature,
            "pressure": pressure,
            "level": level,
            "flow": flow,
            "fault_type": "LOW_LEVEL",
        }
    )


def generate_low_flow_data(count, rng):
    temperature = rng.normal(165, 8, count)
    pressure = rng.normal(6, 0.7, count)
    level = rng.normal(65, 5, count)
    flow = rng.normal(7, 2, count)

    temperature = np.clip(temperature, 140, 185)
    pressure = np.clip(pressure, 4, 8)
    level = np.clip(level, 50, 80)
    flow = np.clip(flow, 2, 12)

    return pd.DataFrame(
        {
            "temperature": temperature,
            "pressure": pressure,
            "level": level,
            "flow": flow,
            "fault_type": "LOW_FLOW",
        }
    )


def generate_dataset():
    rng = np.random.default_rng(RANDOM_SEED)

    normal = generate_normal_data(
        TOTAL_NORMAL_SAMPLES,
        rng,
    )

    high_pressure = generate_high_pressure_data(
        FAULT_SAMPLES_PER_TYPE,
        rng,
    )

    high_temperature = generate_high_temperature_data(
        FAULT_SAMPLES_PER_TYPE,
        rng,
    )

    low_level = generate_low_level_data(
        FAULT_SAMPLES_PER_TYPE,
        rng,
    )

    low_flow = generate_low_flow_data(
        FAULT_SAMPLES_PER_TYPE,
        rng,
    )

    dataset = pd.concat(
        [
            normal,
            high_pressure,
            high_temperature,
            low_level,
            low_flow,
        ],
        ignore_index=True,
    )

    dataset = dataset.sample(
        frac=1,
        random_state=RANDOM_SEED,
    ).reset_index(drop=True)

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True,
    )

    dataset.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("Dataset generation complete.")
    print()
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Total samples: {len(dataset)}")
    print()
    print("Samples by fault type:")
    print(dataset["fault_type"].value_counts())
    print()
    print("Dataset preview:")
    print(dataset.head())


if __name__ == "__main__":
    generate_dataset()
