# check the mlruns
# get the best results
# load that model 
# push to gcp registry
import mlflow
from tensorflow.keras.models import load_model

def get_best_model_and_load_weights(experiment_names):
    mlflow.set_tracking_uri("http://localhost:5000")  # Set to your MLflow tracking URI

    best_rmse = float('inf')
    best_model_uri = None
    best_experiment_name = None
    best_run_id = None

    # Loop through each experiment to find the best model
    for experiment_name in experiment_names:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            print(f"Experiment '{experiment_name}' not found.")
            continue
        experiment_id = experiment.experiment_id

        # Get all runs for the current experiment
        runs = mlflow.search_runs(experiment_ids=[experiment_id])
        if runs.empty:
            print(f"No runs found for experiment '{experiment_name}'.")
            continue

        # Identify the run with the lowest RMSE in this experiment
        best_run_in_experiment = runs.loc[runs['metrics.validation_rmse'].idxmin()]
        current_rmse = best_run_in_experiment['metrics.validation_rmse']

        if current_rmse < best_rmse:
            best_rmse = current_rmse
            best_model_uri = f"runs:/{best_run_in_experiment['run_id']}/model"
            best_experiment_name = experiment_name
            best_run_id = best_run_in_experiment['run_id']

    if best_model_uri:
        # Load the best model architecture
        print(f"Best model found in experiment '{best_experiment_name}' with run ID '{best_run_id}'")
        print(f"Validation RMSE: {best_rmse}")
        model = mlflow.keras.load_model(best_model_uri)

        # Download weights from MLflow and load into the model
        weights_path = mlflow.artifacts.download_artifacts(f"runs:/{best_run_id}/model_weights.h5")
        model.load_weights(weights_path)
        
        return model, best_rmse, best_experiment_name, best_run_id
    else:
        print("No valid models found across experiments.")
        return None, None, None, None

# Usage
experiment_names = ["PM2.5 Random Forest", "PM2.5 XGBoost Prediction", "PM2.5 Prophet", "PM 2.5 LSTM Predict"]
best_model, best_rmse, best_experiment_name, best_run_id = get_best_model_and_load_weights(experiment_names)

if best_model:
    print(f"Loaded best model with weights from experiment '{best_experiment_name}' and RMSE: {best_rmse}")

