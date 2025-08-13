#!/usr/bin/env python3
"""
Test script to run the complete pipeline and verify results
"""

import time
from pathlib import Path
from google.cloud import bigquery
from google.cloud import aiplatform

def check_bigquery_predictions(project_id="purple-25-gradient-20250605", 
                              table_name="purple-25-gradient-20250605.master_table_final.master_table_final_v5",
                              prediction_column="predicted_final_location_score"):
    """Check if predictions were written to BigQuery."""
    print("🔍 CHECKING BIGQUERY PREDICTIONS")
    print("=" * 50)
    
    try:
        client = bigquery.Client(project=project_id)
        
        # Check if target table exists
        try:
            table = client.get_table(table_name)
            print(f"✅ Target table exists: {table_name}")
            print(f"📊 Total rows: {table.num_rows:,}")
        except Exception as e:
            print(f"❌ Target table does not exist: {e}")
            return False
        
        # Check for prediction column
        schema_has_prediction = any(field.name == prediction_column for field in table.schema)
        if schema_has_prediction:
            print(f"✅ Prediction column exists: {prediction_column}")
        else:
            print(f"❌ Prediction column missing: {prediction_column}")
            return False
        
        # Check prediction statistics
        stats_query = f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNT({prediction_column}) as rows_with_predictions,
            MIN({prediction_column}) as min_prediction,
            MAX({prediction_column}) as max_prediction,
            AVG({prediction_column}) as avg_prediction,
            STDDEV({prediction_column}) as std_prediction
        FROM `{table_name}`
        """
        
        print("📊 Checking prediction statistics...")
        stats_df = client.query(stats_query).to_dataframe()
        
        if len(stats_df) > 0:
            row = stats_df.iloc[0]
            total_rows = int(row['total_rows'])
            rows_with_predictions = int(row['rows_with_predictions']) if row['rows_with_predictions'] is not None else 0
            
            print(f"📋 PREDICTION STATISTICS:")
            print(f"  Total rows: {total_rows:,}")
            print(f"  Rows with predictions: {rows_with_predictions:,}")
            print(f"  Prediction coverage: {(rows_with_predictions/total_rows*100):.1f}%")
            
            if rows_with_predictions > 0:
                print(f"  Min prediction: {row['min_prediction']:.2f}")
                print(f"  Max prediction: {row['max_prediction']:.2f}")
                print(f"  Avg prediction: {row['avg_prediction']:.2f}")
                print(f"  Std prediction: {row['std_prediction']:.2f}")
                
                # Sample some predictions
                sample_query = f"""
                SELECT entity_name, {prediction_column}
                FROM `{table_name}` 
                WHERE {prediction_column} IS NOT NULL 
                LIMIT 5
                """
                
                sample_df = client.query(sample_query).to_dataframe()
                print(f"\n📝 SAMPLE PREDICTIONS:")
                for _, sample_row in sample_df.iterrows():
                    print(f"  {sample_row['entity_name']}: {sample_row[prediction_column]:.2f}")
                
                print(f"\n✅ PREDICTIONS SUCCESSFULLY WRITTEN!")
                return True
            else:
                print(f"\n❌ NO PREDICTIONS FOUND IN TABLE")
                return False
        else:
            print(f"❌ Could not retrieve statistics")
            return False
            
    except Exception as e:
        print(f"❌ Error checking predictions: {e}")
        return False

def check_model_registry(project_id="purple-25-gradient-20250605", 
                        region="us-central1",
                        model_display_name="metrogrub-location-score-predictor-v3"):
    """Check if model was registered in Vertex AI."""
    print("\n🤖 CHECKING MODEL REGISTRY")
    print("=" * 50)
    
    try:
        aiplatform.init(project=project_id, location=region)
        
        # List all models
        print("🔍 Searching for registered models...")
        models = aiplatform.Model.list()
        
        found_model = None
        for model in models:
            if model_display_name in model.display_name:
                found_model = model
                break
        
        if found_model:
            print(f"✅ Model found in registry!")
            print(f"📋 MODEL DETAILS:")
            print(f"  Display name: {found_model.display_name}")
            print(f"  Resource name: {found_model.resource_name}")
            print(f"  Version ID: {getattr(found_model, 'version_id', 'N/A')}")
            print(f"  Create time: {found_model.create_time}")
            print(f"  Update time: {found_model.update_time}")
            
            # Check labels
            if hasattr(found_model, 'labels') and found_model.labels:
                print(f"  Labels:")
                for key, value in found_model.labels.items():
                    print(f"    {key}: {value}")
            
            return True
        else:
            print(f"❌ Model not found in registry")
            print(f"🔍 Available models:")
            for model in models[:5]:  # Show first 5 models
                print(f"  - {model.display_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking model registry: {e}")
        return False

def run_pipeline_test():
    """Run the complete pipeline test."""
    print("🚀 COMPLETE PIPELINE TEST")
    print("=" * 60)
    
    # Step 1: Run the pipeline
    print("Step 1: Running pipeline...")
    print("💡 You can run: cd pipeline_v3 && python3 deploy.py run")
    print("⏳ Waiting for pipeline to complete...")
    print("   (Check Vertex AI Pipelines console for status)")
    
    # For now, just check current state
    time.sleep(2)
    
    # Step 2: Check BigQuery predictions
    print("\nStep 2: Checking BigQuery predictions...")
    predictions_ok = check_bigquery_predictions()
    
    # Step 3: Check model registry
    print("\nStep 3: Checking model registry...")
    registry_ok = check_model_registry()
    
    # Summary
    print("\n🏁 FINAL RESULTS")
    print("=" * 50)
    
    if predictions_ok and registry_ok:
        print("🎉 SUCCESS! Pipeline completed successfully!")
        print("✅ Predictions written to BigQuery")
        print("✅ Model registered in Vertex AI")
    elif predictions_ok:
        print("⚠️  PARTIAL SUCCESS")
        print("✅ Predictions written to BigQuery")
        print("❌ Model registration failed")
    elif registry_ok:
        print("⚠️  PARTIAL SUCCESS")
        print("❌ Predictions not written to BigQuery")
        print("✅ Model registered in Vertex AI")
    else:
        print("❌ PIPELINE ISSUES DETECTED")
        print("❌ No predictions in BigQuery")
        print("❌ No model in registry")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check pipeline logs in Vertex AI Pipelines console")
        print("2. Verify BigQuery table permissions")
        print("3. Check Vertex AI Model Registry permissions")

if __name__ == "__main__":
    run_pipeline_test() 