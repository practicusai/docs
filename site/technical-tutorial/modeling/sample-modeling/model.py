import os
import pandas as pd
from xgboost import XGBRegressor

model = None


async def init(*args, **kwargs):
    print("Initializing model")
    global model

    current_dir = os.path.dirname(__file__)
    model_file = os.path.join(current_dir, "model.ubj")
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"Could not locate model file: {model_file}")

    model = XGBRegressor()
    model.load_model(model_file)


async def predict(df, *args, **kwargs):
    if df is None:
        raise ValueError("No dataframe received")

    X = df[["Temperature"]]

    # Generate predictions
    predictions = model.predict(X)

    # Return predictions as a new DataFrame
    return pd.DataFrame({"predictions": predictions})
