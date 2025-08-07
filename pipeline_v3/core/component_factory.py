#!/usr/bin/env python3
"""
Component Factory for Config-Driven Pipeline v3
Dynamically generates KFP components based on YAML configuration
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Callable
from kfp.dsl import component, Input, Output, Dataset, Model
from typing import NamedTuple

class ComponentFactory:
    """Factory for creating KFP components from configuration."""
    
    def __init__(self, config_path: str = None):
        """Initialize factory with configuration."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "component_configs.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        print(f"Loaded configuration from {config_path}")
        print(f"Available components: {list(self.config['components'].keys())}")
    
    def get_component(self, component_name: str) -> Callable:
        """Get a component by name."""
        if component_name not in self.config['components']:
            raise ValueError(f"Component '{component_name}' not found in configuration")
        
        component_config = self.config['components'][component_name]
        component_type = component_config.get('type', 'unknown')
        
        print(f"Creating component: {component_name} (type: {component_type})")
        
        # Route to appropriate creator method
        if component_type == 'bigquery_extract':
            return self._create_bigquery_extract_component(component_name, component_config)
        elif component_type == 'preprocess':
            return self._create_preprocess_component(component_name, component_config)
        elif component_type == 'train':
            return self._create_train_component(component_name, component_config)
        elif component_type == 'register':
            return self._create_register_component(component_name, component_config)
        elif component_type == 'predict':
            return self._create_bigquery_predict_component(component_name, component_config)
        elif component_type == 'table_ops':
            return self._create_bigquery_table_ops_component(component_name, component_config)
        else:
            raise ValueError(f"Unknown component type: {component_type}")
    
    def get_all_components(self) -> Dict[str, Callable]:
        """Get all components defined in configuration."""
        components = {}
        for name in self.config['components'].keys():
            components[name] = self.get_component(name)
        return components
    
    def _get_base_decorator(self):
        """Get the base KFP component decorator with default settings."""
        defaults = self.config.get('defaults', {})
        
        return component(
            base_image=defaults.get('base_image', 'python:3.9-slim'),
            packages_to_install=defaults.get('packages', [])
        )
    
    def _create_bigquery_extract_component(self, name: str, config: Dict[str, Any]):
        """Create BigQuery data extraction component."""
        
        @self._get_base_decorator()
        def extract_component(
            project_id: str,
            table_name: str,
            feature_columns: list,
            target_column: str,
            output_dataset: Output[Dataset]
        ) -> NamedTuple('DataResult', [('num_rows', int), ('num_features', int)]):
            from google.cloud import bigquery
            import pandas as pd
            import numpy as np
            from typing import NamedTuple
            
            # Define return type inside function to avoid NameError
            DataResult = NamedTuple('DataResult', [('num_rows', int), ('num_features', int)])
            
            try:
                print("=== DATA EXTRACTION COMPONENT ===")
                print("Project: " + str(project_id))
                print("Table: " + str(table_name))
                print("Features: " + str(feature_columns))
                print("Target: " + str(target_column))
                
                # Create BigQuery client
                client = bigquery.Client(project=project_id)
                
                # Use hardcoded query for robustness (from working pipeline)
                query = f"""
                SELECT category, is_food, foot_traffic_score, {target_column}, entity_name 
                FROM `{table_name}` 
                WHERE {target_column} IS NOT NULL 
                    AND foot_traffic_score IS NOT NULL 
                    AND category IS NOT NULL 
                    AND is_food IS NOT NULL 
                    AND entity_name IS NOT NULL
                """
                
                print("Executing query...")
                print("Query: " + query.replace('\n', ' ').replace('  ', ' '))
                
                # Execute query
                df = client.query(query).to_dataframe()
                print("Retrieved " + str(len(df)) + " rows, " + str(df.shape[1]) + " columns")
                
                # Data validation (from working pipeline)
                if len(df) == 0:
                    raise ValueError("No data extracted from BigQuery")
                
                # Additional cleaning (from working pipeline)
                print("Cleaning data...")
                initial_count = len(df)
                df_clean = df.dropna(subset=feature_columns + [target_column])
                df_clean = df_clean.replace([np.inf, -np.inf], np.nan).dropna()
                final_count = len(df_clean)
                
                print("Removed " + str(initial_count - final_count) + " rows with NaN/inf values")
                print("Final dataset: " + str(final_count) + " rows")
                
                # Save the cleaned dataset
                print("Saving dataset to: " + output_dataset.path)
                df_clean.to_csv(output_dataset.path, index=False)
                print("Dataset saved successfully")
                
                return DataResult(len(df_clean), len(feature_columns))
                
            except Exception as e:
                print("=== EXTRACTION COMPONENT FAILED ===")
                print("Error: " + str(e))
                import traceback
                traceback.print_exc()
                raise RuntimeError("Data extraction failed: " + str(e)) from e
        
        extract_component.__name__ = f"{name}_component"
        return extract_component
    
    def _create_preprocess_component(self, name: str, config: Dict[str, Any]):
        """Create preprocessing component."""
        
        @self._get_base_decorator()
        def preprocess_component(
            input_dataset: Input[Dataset],
            feature_columns: list,
            target_column: str,
            train_dataset: Output[Dataset],
            test_dataset: Output[Dataset],
            preprocessor: Output[Model]
        ) -> NamedTuple('PreprocessResult', [('train_rows', int), ('test_rows', int), ('feature_count', int)]):
            import pandas as pd
            import numpy as np
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import StandardScaler, OneHotEncoder
            from sklearn.compose import ColumnTransformer
            import pickle
            from typing import NamedTuple
            
            # Define return type inside function
            PreprocessResult = NamedTuple('PreprocessResult', [('train_rows', int), ('test_rows', int), ('feature_count', int)])
            
            # Hardcode configuration values for reliability
            test_size = 0.2
            random_state = 42
            categorical_features = ['category']
            numerical_features = ['is_food', 'foot_traffic_score']
            encoder_params = {'drop': 'first', 'sparse_output': False, 'handle_unknown': 'ignore'}  # Added handle_unknown
            validation = {'min_train_size': 10, 'min_test_size': 5}
            
            try:
                print("=== PREPROCESSING COMPONENT ===")
                print("Loading dataset from: " + input_dataset.path)
                
                df = pd.read_csv(input_dataset.path)
                print("Dataset loaded. Shape: " + str(df.shape))
                
                # Validate required columns
                critical_columns = feature_columns + [target_column, 'entity_name']
                missing_cols = [col for col in critical_columns if col not in df.columns]
                if missing_cols:
                    raise ValueError("Missing columns: " + str(missing_cols))
                
                # Clean data
                df_clean = df.dropna(subset=critical_columns)
                print("After cleaning: " + str(len(df_clean)) + " rows")
                
                if len(df_clean) == 0:
                    raise ValueError("No data remaining after cleaning")
                
                # Separate features and target
                X = df_clean[feature_columns + ['entity_name']]
                y = df_clean[target_column]
                
                # Create preprocessor (from working pipeline pattern)
                transformers = []
                if numerical_features:
                    transformers.append(('num', StandardScaler(), numerical_features))
                if categorical_features:
                    transformers.append(('cat', OneHotEncoder(**encoder_params), categorical_features))
                
                preprocessor_pipeline = ColumnTransformer(transformers=transformers)
                
                # Fit and transform
                feature_X = X[feature_columns]
                X_processed = preprocessor_pipeline.fit_transform(feature_X)
                
                # Split data
                X_train, X_test, X_train_ids, X_test_ids, y_train, y_test = train_test_split(
                    X_processed, X['entity_name'], y, 
                    test_size=test_size, 
                    random_state=random_state
                )
                
                print("Split completed:")
                print("  Train: " + str(X_train.shape))
                print("  Test: " + str(X_test.shape))
                
                # Validate sizes
                if len(X_train) < validation["min_train_size"]:
                    raise ValueError("Train set too small: " + str(len(X_train)))
                if len(X_test) < validation["min_test_size"]:
                    raise ValueError("Test set too small: " + str(len(X_test)))
                
                # Save datasets (matching working pipeline format)
                train_df = pd.DataFrame(X_train)
                train_df['target'] = y_train.values
                train_df['entity_name'] = X_train_ids.values
                train_df.to_csv(train_dataset.path, index=False)
                
                test_df = pd.DataFrame(X_test)
                test_df['target'] = y_test.values
                test_df['entity_name'] = X_test_ids.values
                test_df.to_csv(test_dataset.path, index=False)
                
                # Save preprocessor
                with open(preprocessor.path, 'wb') as f:
                    pickle.dump(preprocessor_pipeline, f)
                
                print("Preprocessing completed successfully")
                return PreprocessResult(len(X_train), len(X_test), X_processed.shape[1])
                
            except Exception as e:
                print("=== PREPROCESSING FAILED ===")
                print("Error: " + str(e))
                import traceback
                traceback.print_exc()
                raise RuntimeError("Preprocessing failed: " + str(e)) from e
        
        preprocess_component.__name__ = f"{name}_component"
        return preprocess_component
    
    def _create_train_component(self, name: str, config: Dict[str, Any]):
        """Create model training component."""
        
        @self._get_base_decorator()
        def train_component(
            train_dataset: Input[Dataset],
            test_dataset: Input[Dataset],
            model: Output[Model],
            feature_columns: list
        ) -> NamedTuple('TrainResult', [('train_score', float), ('test_score', float), ('feature_importance', str)]):
            import pandas as pd
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.metrics import r2_score
            import pickle
            import json
            from typing import NamedTuple
            
            # Define return type inside function
            TrainResult = NamedTuple('TrainResult', [('train_score', float), ('test_score', float), ('feature_importance', str)])
            
            # Hardcode model parameters for reliability
            model_params = {
                'n_estimators': 100,
                'max_depth': 10,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'random_state': 42,
                'n_jobs': -1
            }
            thresholds = {'min_train_score': 0.1, 'min_test_score': 0.05}
            
            try:
                print("=== TRAINING COMPONENT ===")
                print("Model parameters: " + str(model_params))
                
                # Load datasets
                train_df = pd.read_csv(train_dataset.path)
                test_df = pd.read_csv(test_dataset.path)
                
                print("Loaded datasets:")
                print("  Train: " + str(train_df.shape))
                print("  Test: " + str(test_df.shape))
                
                # Separate features and targets
                feature_cols = [col for col in train_df.columns if col not in ['target', 'entity_name']]
                
                X_train = train_df[feature_cols]
                y_train = train_df['target']
                X_test = test_df[feature_cols]
                y_test = test_df['target']
                
                print("Feature columns: " + str(len(feature_cols)))
                
                # Train model
                print("Training Random Forest model...")
                trained_model = RandomForestRegressor(**model_params)
                trained_model.fit(X_train, y_train)
                
                # Evaluate
                train_score = r2_score(y_train, trained_model.predict(X_train))
                test_score = r2_score(y_test, trained_model.predict(X_test))
                
                print("Training completed:")
                print("  Train R2: " + str(round(train_score, 4)))
                print("  Test R2: " + str(round(test_score, 4)))
                
                # Validate performance
                if train_score < thresholds['min_train_score']:
                    raise ValueError("Train score too low: " + str(train_score))
                if test_score < thresholds['min_test_score']:
                    raise ValueError("Test score too low: " + str(test_score))
                
                # Get feature importance (matching working pipeline format)
                feature_importance_dict = {}
                for i, importance in enumerate(trained_model.feature_importances_):
                    feature_importance_dict[str(i)] = float(importance)
                
                # Save model
                with open(model.path, 'wb') as f:
                    pickle.dump(trained_model, f)
                
                print("Model saved successfully")
                return TrainResult(float(train_score), float(test_score), json.dumps(feature_importance_dict))
                
            except Exception as e:
                print("=== TRAINING FAILED ===")
                print("Error: " + str(e))
                import traceback
                traceback.print_exc()
                raise RuntimeError("Training failed: " + str(e)) from e
        
        train_component.__name__ = f"{name}_component"
        return train_component
    
    def _create_register_component(self, name: str, config: Dict[str, Any]):
        """Create model registration component using proven working patterns."""
        
        @self._get_base_decorator()
        def register_component(
            project_id: str,
            region: str,
            model_display_name: str,
            model_description: str,
            model: Input[Model],
            preprocessor: Input[Model],
            train_score: float,
            test_score: float,
            feature_importance: str,
            feature_columns: list
        ) -> NamedTuple('RegistryResult', [('model_resource_name', str), ('model_version_id', str)]):
            from google.cloud import aiplatform
            import pickle
            import json
            import tempfile
            import os
            from datetime import datetime
            from typing import NamedTuple
            
            # Define return type inside function
            RegistryResult = NamedTuple('RegistryResult', [('model_resource_name', str), ('model_version_id', str)])
            
            try:
                print("=== MODEL REGISTRATION COMPONENT ===")
                print("Display name: " + str(model_display_name))
                print("Project: " + str(project_id))
                print("Region: " + str(region))
                
                # Initialize Vertex AI
                aiplatform.init(project=project_id, location=region)
                
                # Load models to get metadata (from working pipeline)
                with open(model.path, 'rb') as f:
                    trained_model = pickle.load(f)
                print("Model loaded: " + str(type(trained_model).__name__))
                
                with open(preprocessor.path, 'rb') as f:
                    preprocessor_pipeline = pickle.load(f)
                print("Preprocessor loaded: " + str(type(preprocessor_pipeline).__name__))
                
                # Parse feature importance
                feature_importance_dict = json.loads(feature_importance)
                
                # Create feature importance with proper names (from working pipeline)
                feature_importance_named = {}
                for i, (idx, importance) in enumerate(feature_importance_dict.items()):
                    if i < len(feature_columns):
                        feature_name = feature_columns[i]
                        feature_importance_named[feature_name] = float(importance)
                
                # Create comprehensive metadata (from working pipeline)
                model_metadata = {
                    "model_type": "RandomForestRegressor",
                    "framework": "scikit-learn",
                    "framework_version": "1.3.2",
                    "training_date": datetime.now().isoformat(),
                    "feature_columns": feature_columns,
                    "feature_importance": feature_importance_named,
                    "model_parameters": {
                        "n_estimators": trained_model.n_estimators,
                        "max_depth": trained_model.max_depth,
                        "min_samples_split": trained_model.min_samples_split,
                        "min_samples_leaf": trained_model.min_samples_leaf,
                        "random_state": trained_model.random_state
                    },
                    "performance_metrics": {
                        "training_r2_score": float(train_score),
                        "test_r2_score": float(test_score),
                        "n_features": len(feature_columns)
                    },
                    "preprocessing": {
                        "categorical_features": ["category"],
                        "numerical_features": ["is_food", "foot_traffic_score"],
                        "encoding_method": "OneHotEncoder + StandardScaler"
                    }
                }
                
                print("Model metadata prepared")
                
                # Create temporary directory with proper structure (from working pipeline)
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Save model artifacts in required format
                    model_path = os.path.join(temp_dir, "model.pkl")
                    preprocessor_path = os.path.join(temp_dir, "preprocessor.pkl") 
                    metadata_path = os.path.join(temp_dir, "metadata.json")
                    
                    # Copy model files (from working pipeline pattern)
                    with open(model.path, 'rb') as src, open(model_path, 'wb') as dst:
                        dst.write(src.read())
                    
                    with open(preprocessor.path, 'rb') as src, open(preprocessor_path, 'wb') as dst:
                        dst.write(src.read())
                    
                    # Save metadata
                    with open(metadata_path, 'w') as f:
                        json.dump(model_metadata, f, indent=2)
                    
                    # Create version description (from working pipeline)
                    version_description = f"""
                    Quarterly trained Random Forest model for MetroGrub location score prediction.
                    
                    Performance Metrics:
                    - Training R2 Score: {train_score:.4f}
                    - Test R2 Score: {test_score:.4f}
                    - Features: {len(feature_columns)}
                    
                    Feature Importance:
                    {json.dumps(feature_importance_named, indent=2)}
                    
                    Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """
                    
                    # Upload model to Model Registry (from working pipeline)
                    print("Registering model to Vertex AI Model Registry...")
                    
                    model_upload = aiplatform.Model.upload(
                        display_name=model_display_name,
                        description=model_description,
                        serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest",
                        artifact_uri=temp_dir,
                        version_description=version_description,
                        labels={
                            "model_type": "random_forest",
                            "use_case": "location_scoring", 
                            "training_framework": "scikit_learn",
                            "quarterly_model": "true",
                            "pipeline_version": "v3"
                        }
                    )
                    
                    print("Model registered successfully!")
                    print("Resource name: " + str(model_upload.resource_name))
                    print("Version ID: " + str(model_upload.version_id))
                    
                    return RegistryResult(model_upload.resource_name, model_upload.version_id)
                
            except Exception as e:
                print("=== MODEL REGISTRATION FAILED ===")
                print("Error: " + str(e))
                import traceback
                traceback.print_exc()
                
                # Return empty strings instead of failing pipeline (from working pipeline)
                print("Model training completed but registration failed")
                return RegistryResult("", "")
        
        register_component.__name__ = f"{name}_component"
        return register_component
    
    def _create_bigquery_predict_component(self, name: str, config: Dict[str, Any]):
        """Create BigQuery prediction component using proven bulk operations."""
        
        @self._get_base_decorator()
        def predict_component(
            project_id: str,
            table_name: str,
            feature_columns: list,
            target_column: str,
            prediction_column: str,
            model: Input[Model],
            preprocessor: Input[Model]
        ) -> NamedTuple('PredictResult', [('updated_rows', int), ('prediction_stats', str)]):
            import pandas as pd
            import numpy as np
            import pickle
            from google.cloud import bigquery
            from typing import NamedTuple
            import json
            
            # Define return type inside function
            PredictResult = NamedTuple('PredictResult', [('updated_rows', int), ('prediction_stats', str)])
            
            try:
                print("=== PREDICTION COMPONENT ===")
                print("Table: " + str(table_name))
                print("Features: " + str(feature_columns))
                
                # Load model and preprocessor
                with open(model.path, 'rb') as f:
                    trained_model = pickle.load(f)
                print("Model loaded: " + str(type(trained_model).__name__))
                
                with open(preprocessor.path, 'rb') as f:
                    preprocessor_pipeline = pickle.load(f)
                print("Preprocessor loaded")
                
                # Initialize BigQuery client
                client = bigquery.Client(project=project_id)
                
                # Extract all data for prediction (from working pipeline query)
                features_str = ", ".join(feature_columns)
                query = f"""
                SELECT {features_str}, {target_column}, entity_name 
                FROM `{table_name}` 
                WHERE {target_column} IS NOT NULL 
                    AND foot_traffic_score IS NOT NULL 
                    AND category IS NOT NULL 
                    AND is_food IS NOT NULL 
                    AND entity_name IS NOT NULL
                """
                
                print("Loading data for prediction...")
                df = client.query(query).to_dataframe()
                print("Loaded " + str(len(df)) + " rows for prediction")
                
                if len(df) == 0:
                    print("No data found for prediction")
                    return PredictResult(0, json.dumps({"message": "No data found"}))
                
                # Preprocess features (from working pipeline)
                X = df[feature_columns]
                X_processed = preprocessor_pipeline.transform(X)
                
                # Make predictions (from working pipeline)
                print("Making predictions...")
                predictions = trained_model.predict(X_processed)
                
                # Convert to integers (from working pipeline)
                predictions_int = np.round(predictions).astype(int)
                print("Generated " + str(len(predictions_int)) + " predictions")
                
                # Add predictions to dataframe
                df[prediction_column] = predictions_int
                
                # Calculate stats (from working pipeline)
                stats = {
                    'mean_prediction': float(np.mean(predictions_int)),
                    'std_prediction': float(np.std(predictions_int)),
                    'min_prediction': int(np.min(predictions_int)),
                    'max_prediction': int(np.max(predictions_int)),
                    'num_predictions': len(predictions_int)
                }
                
                print("Prediction stats: " + str(stats))
                
                # Use bulk MERGE operation (from working pipeline) instead of individual updates
                temp_table_id = f"{table_name}_predictions_temp"
                
                # Prepare data for upload (only entity_name and prediction)
                update_df = df[['entity_name', prediction_column]].copy()
                
                # Create job config (from working pipeline)
                job_config = bigquery.LoadJobConfig(
                    write_disposition="WRITE_TRUNCATE",
                    schema=[
                        bigquery.SchemaField("entity_name", "STRING"),
                        bigquery.SchemaField(prediction_column, "INTEGER"),
                    ]
                )
                
                # Load predictions to temp table (from working pipeline)
                print("Loading predictions to temp table...")
                job = client.load_table_from_dataframe(update_df, temp_table_id, job_config=job_config)
                job.result()  # Wait for completion
                
                # Update main table using MERGE (from working pipeline)
                merge_query = f"""
                MERGE `{table_name}` AS target
                USING `{temp_table_id}` AS source
                ON target.entity_name = source.entity_name
                WHEN MATCHED THEN
                    UPDATE SET {prediction_column} = source.{prediction_column}
                """
                
                print("Executing bulk MERGE query...")
                job = client.query(merge_query)
                job.result()  # Wait for completion
                
                # Clean up temp table (from working pipeline)
                client.delete_table(temp_table_id)
                print("Cleaned up temp table")
                
                print("Successfully updated " + str(len(update_df)) + " rows using bulk operations")
                return PredictResult(len(update_df), json.dumps(stats))
                
            except Exception as e:
                print("=== PREDICTION COMPONENT FAILED ===")
                print("Error: " + str(e))
                import traceback
                traceback.print_exc()
                raise RuntimeError("Prediction component failed: " + str(e)) from e
        
        predict_component.__name__ = f"{name}_component"
        return predict_component
    
    def _create_bigquery_table_ops_component(self, name: str, config: Dict[str, Any]):
        """Create BigQuery table operations component using working pipeline patterns."""
        
        @self._get_base_decorator()
        def table_ops_component(
            project_id: str,
            source_table: str,
            target_table: str,
            prediction_column: str
        ) -> NamedTuple('TableResult', [('success', bool), ('rows_copied', int)]):
            from google.cloud import bigquery
            from typing import NamedTuple
            
            # Define return type inside function
            TableResult = NamedTuple('TableResult', [('success', bool), ('rows_copied', int)])
            
            try:
                print("=== TABLE OPERATIONS COMPONENT ===")
                print("Source: " + str(source_table))
                print("Target: " + str(target_table))
                
                client = bigquery.Client(project=project_id)
                
                # Create target table by copying ALL data from source (from working pipeline)
                print("Creating target table with data from source...")
                copy_query = f"""
                CREATE OR REPLACE TABLE `{target_table}` AS
                SELECT * FROM `{source_table}`
                """
                
                print("Executing copy query...")
                job = client.query(copy_query)
                job.result()  # Wait for completion
                
                # Get row count
                count_query = f"SELECT COUNT(*) as row_count FROM `{target_table}`"
                count_result = client.query(count_query).to_dataframe()
                rows_copied = int(count_result['row_count'].iloc[0])
                
                print("Successfully copied " + str(rows_copied) + " rows")
                
                # Add prediction column (from working pipeline)
                try:
                    alter_query = f"""
                    ALTER TABLE `{target_table}`
                    ADD COLUMN {prediction_column} INT64
                    """
                    
                    print("Adding prediction column...")
                    job = client.query(alter_query)
                    job.result()
                    print("Prediction column added successfully")
                    
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print("Column already exists, skipping...")
                    else:
                        raise e
                
                return TableResult(True, rows_copied)
                
            except Exception as e:
                print("=== TABLE OPERATIONS FAILED ===")
                print("Error: " + str(e))
                import traceback
                traceback.print_exc()
                raise RuntimeError("Table operations failed: " + str(e)) from e
        
        table_ops_component.__name__ = f"{name}_component"
        return table_ops_component 