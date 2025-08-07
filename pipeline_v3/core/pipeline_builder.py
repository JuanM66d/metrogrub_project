"""
Constructs KFP pipeline from YAML configuration and component factory.
"""
import yaml
from typing import Dict, Any
from kfp.dsl import pipeline
from pathlib import Path
from .component_factory import ComponentFactory

class PipelineBuilder:
    """Builds Kubeflow Pipeline from configuration."""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "component_configs.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.factory = ComponentFactory(config_path)
        self.pipeline_config = self.config["pipeline"]
        self.flow_config = self.config["pipeline_flow"]
    
    def build_pipeline(self):
        """Build the complete KFP pipeline from configuration."""
        
        @pipeline(
            name=self.pipeline_config["name"],
            description=self.pipeline_config["description"],
            pipeline_root="gs://purple-25-gradient-20250605-vertex-ai-pipelines/pipeline_root"
        )
        def config_driven_pipeline(
            project_id: str = "purple-25-gradient-20250605",
            source_table: str = "purple-25-gradient-20250605.master_table_final.master_table_final_v3",
            target_table: str = "purple-25-gradient-20250605.master_table_final.master_table_final_v5", 
            feature_columns: list = ["category", "is_food", "foot_traffic_score"],
            target_column: str = "final_location_score",
            prediction_column: str = "predicted_final_location_score",
            model_display_name: str = "metrogrub-location-score-predictor-v3",
            model_description: str = "Config-driven Random Forest model for location score prediction (Pipeline v3)",
            region: str = "us-central1"
        ):
            """Auto-generated pipeline from YAML configuration."""
            
            # Get all components from factory
            components = self.factory.get_all_components()
            
            # Build pipeline steps from flow configuration
            step_tasks = {}
            
            for step in self.flow_config["steps"]:
                step_name = step["name"]
                component_name = step["component"]
                step_inputs = step["inputs"]
                
                # Get the component
                component_func = components[component_name]
                
                # Resolve input parameters
                resolved_inputs = self._resolve_inputs(step_inputs, step_tasks, locals())
                
                # Create and execute the step
                step_task = component_func(**resolved_inputs)
                
                # Handle dependencies
                if "depends_on" in step:
                    for dependency in step["depends_on"]:
                        if dependency in step_tasks:
                            step_task.after(step_tasks[dependency])
                
                # Store task for future reference
                step_tasks[step_name] = step_task
            
            # Don't return anything - KFP pipeline functions shouldn't return tasks
            return None
        
        return config_driven_pipeline
    
    def _resolve_inputs(self, step_inputs: Dict[str, Any], step_tasks: Dict[str, Any], pipeline_params: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve input parameters, handling variable substitution and task outputs."""
        resolved = {}
        
        for input_name, input_value in step_inputs.items():
            if isinstance(input_value, str):
                if input_value.startswith("${") and input_value.endswith("}"):
                    # Pipeline parameter substitution
                    param_name = input_value[2:-1]  # Remove ${ and }
                    resolved[input_name] = pipeline_params.get(param_name, input_value)
                elif ".outputs[" in input_value:
                    # Task output reference (e.g., "extract_data.outputs['dataset']")
                    task_name = input_value.split(".outputs[")[0]
                    output_name = input_value.split("'")[1]  # Extract name from ['dataset']
                    if task_name in step_tasks:
                        resolved[input_name] = step_tasks[task_name].outputs[output_name]
                    else:
                        resolved[input_name] = input_value
                elif "." in input_value and not input_value.startswith("gs://"):
                    # Legacy format: "extract_data.dataset" 
                    task_name, output_name = input_value.split(".", 1)
                    if task_name in step_tasks:
                        resolved[input_name] = step_tasks[task_name].outputs[output_name]
                    else:
                        resolved[input_name] = input_value
                else:
                    # Literal string value
                    resolved[input_name] = input_value
            else:
                # Non-string value (list, dict, etc.)
                resolved[input_name] = input_value
        
        return resolved
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get pipeline metadata and configuration summary."""
        return {
            "name": self.pipeline_config["name"],
            "description": self.pipeline_config["description"],
            "version": self.pipeline_config["version"],
            "components": list(self.config["components"].keys()),
            "steps": [step["name"] for step in self.flow_config["steps"]],
            "total_components": len(self.config["components"]),
            "total_steps": len(self.flow_config["steps"])
        }
    
    def validate_configuration(self) -> bool:
        """Validate the pipeline configuration."""
        errors = []
        
        # Check required sections
        required_sections = ["pipeline", "defaults", "components", "pipeline_flow"]
        for section in required_sections:
            if section not in self.config:
                errors.append(f"Missing required section: {section}")
        
        # Check component types
        valid_types = ["bigquery_extract", "preprocess", "train", "register", "predict", "table_ops"]
        for comp_name, comp_config in self.config.get("components", {}).items():
            if "type" not in comp_config:
                errors.append(f"Component {comp_name} missing type")
            elif comp_config["type"] not in valid_types:
                errors.append(f"Unknown component type: {comp_config['type']}")
        
        # Check pipeline flow references
        component_names = set(self.config.get("components", {}).keys())
        for step in self.flow_config.get("steps", []):
            if "component" not in step:
                errors.append(f"Step {step.get('name', 'unnamed')} missing component reference")
            elif step["component"] not in component_names:
                errors.append(f"Step references unknown component: {step['component']}")
        
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print("✅ Configuration validation passed")
        return True
    
    def compile_pipeline(self, output_path: str = "config_driven_pipeline_v3.json"):
        """Compile the config-driven pipeline."""
        import kfp
        
        # Validate first
        if not self.validate_configuration():
            raise ValueError("Configuration validation failed")
        
        # Build pipeline
        pipeline_func = self.build_pipeline()
        
        # Compile
        compiler = kfp.compiler.Compiler()
        compiler.compile(
            pipeline_func=pipeline_func,
            package_path=output_path
        )
        
        print(f"✅ Config-driven pipeline compiled: {output_path}")
        return output_path 