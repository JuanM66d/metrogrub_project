import os
import json
from datetime import datetime
from google.cloud import aiplatform

def trigger_model_pipeline(request):
    """
    Production version of the MetroGrub ML pipeline cloud function.
    Can run in test mode or deploy real pipelines based on configuration.
    """
    print("🚀 Starting MetroGrub Model Pipeline Cloud Function...")
    
    try:
        # Get request data
        request_json = request.get_json(silent=True) or {}
        print(f"📝 Received request: {request_json}")
        
        # Initialize Vertex AI
        project_id = os.environ.get("PROJECT_ID", "purple-25-gradient-20250605")
        location = os.environ.get("LOCATION", "us-central1")
        pipeline_root = os.environ.get("PIPELINE_ROOT", "gs://purple-25-gradient-20250605-vertex-ai-pipelines/pipeline_root")
        service_account = os.environ.get("SERVICE_ACCOUNT", "119856114569-compute@developer.gserviceaccount.com")
        
        aiplatform.init(project=project_id, location=location)
        print(f"✅ Initialized Vertex AI for project: {project_id}")
        
        # Check if we have a pipeline template
        template_path = os.environ.get("TEMPLATE_PATH")
        
        if not template_path:
            # Test mode - no real pipeline deployment
            print("🧪 Running in TEST MODE - no template provided")
            print("✅ Test mode completed successfully!")
            
            response = {
                "status": "success",
                "message": "Test mode completed successfully",
                "mode": "test",
                "timestamp": datetime.now().isoformat(),
                "request_data": request_json,
                "note": "To deploy real pipeline, set TEMPLATE_PATH environment variable"
            }
            
            return json.dumps(response), 200
        
        # Production mode - deploy real pipeline
        print(f"🔧 PRODUCTION MODE - Using template: {template_path}")
        
        # Get parameter overrides from environment variables
        parameters = {}
        
        # Table parameters
        target_table = os.environ.get("TARGET_TABLE")
        if target_table:
            parameters["target_table"] = target_table
            
        source_table = os.environ.get("SOURCE_TABLE") 
        if source_table:
            parameters["source_table"] = source_table
            
        prediction_column = os.environ.get("PREDICTION_COLUMN")
        if prediction_column:
            parameters["prediction_column"] = prediction_column
            
        # Additional pipeline parameters
        enable_caching = os.environ.get("ENABLE_CACHING", "false").lower() == "true"
        
        print(f"🔧 Using parameters: {parameters}")
        
        # Create and submit pipeline job
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        display_name = f"metrogrub-scheduled-pipeline-{timestamp}"
        
        job = aiplatform.PipelineJob(
            display_name=display_name,
            template_path=template_path,
            pipeline_root=pipeline_root,
            parameter_values=parameters,
            enable_caching=enable_caching
        )
        
        # Submit the job (non-blocking)
        print("🚀 Submitting pipeline job...")
        job.run(
            service_account=service_account,
            sync=False  # Don't wait for completion in cloud function
        )
        
        print(f"✅ Pipeline submitted successfully: {display_name}")
        print(f"🔗 Job ID: {job.name}")
        print(f"🔗 View at: https://console.cloud.google.com/vertex-ai/pipelines/runs?project={project_id}")
        
        # Return success response
        response = {
            "status": "success",
            "message": "Pipeline submitted successfully",
            "mode": "production",
            "job_name": job.name,
            "job_display_name": display_name,
            "pipeline_root": pipeline_root,
            "template_path": template_path,
            "parameters": parameters,
            "timestamp": datetime.now().isoformat(),
            "console_url": f"https://console.cloud.google.com/vertex-ai/pipelines/runs?project={project_id}"
        }
        
        return json.dumps(response), 200
        
    except Exception as e:
        error_msg = f"❌ Pipeline execution failed: {str(e)}"
        print(error_msg)
        
        error_response = {
            "status": "error",
            "message": error_msg,
            "error_type": type(e).__name__,
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(error_response), 500

def health_check(request):
    """Simple health check endpoint for the cloud function."""
    return json.dumps({
        "status": "healthy", 
        "function": "model_pipeline",
        "timestamp": datetime.now().isoformat()
    }), 200 