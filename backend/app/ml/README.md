# Crop suggestion model

- `artifacts/` contains the model and label encoder loaded by the API.
- `data/plants.csv` contains the 92-plant recommendation dataset.
- `crop_predictor.py` contains inference-only application code.
- `plant_recommender.py` provides dataset-based top-three recommendations.
- `training/` contains offline dataset generation and training utilities.

Regenerate and train from the `fastapi` directory:

```bash
python -m app.ml.training.generate_dataset
python -m app.ml.training.train_model
```

Generated Python bytecode (`.pyc`) is intentionally excluded.
