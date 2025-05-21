#!/usr/bin/env python3
"""
This script tests the integration of custom plugins with the CVInsight client.
It focuses on ensuring that custom plugin data is correctly extracted and accessible.
"""
import os
import sys
import json
import traceback

# Add the project root to the Python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cvinsight import CVInsightClient

# Import our custom plugins
from cvinsight.custom_plugins import (
    RelevantYoEExtractorPlugin,
    EducationStatsExtractorPlugin,
    WorkStatsExtractorPlugin,
    SocialExtractorPlugin
)

from dotenv import load_dotenv

def pretty_print_dict(data, indent=0):
    """Helper function to print dictionaries in a readable format."""
    for key, value in data.items():
        if isinstance(value, dict):
            print("  " * indent + f"{key}:")
            pretty_print_dict(value, indent + 1)
        else:
            print("  " * indent + f"{key}: {value}")

def main():
    try:
        # Load environment variables and get API key
        load_dotenv()
        api_key = os.environ.get("OPEN_AI_API_KEY")
        
        if not api_key:
            print("Error: OPEN_AI_API_KEY environment variable not found")
            return
            
        print(f"API Key found: {api_key[:5]}...")
        
        # Create Results directory if it doesn't exist
        if not os.path.exists("../Results"):
            os.makedirs("../Results")
            print("Created Results directory")
        
        # Initialize the CVInsight client with OpenAI
        print("\nInitializing CVInsight client...")
        client = CVInsightClient(
            api_key=api_key,
            provider="openai",
            model_name="o4-mini-2025-04-16"
        )
        
        # Register our custom plugins manually
        print("\nRegistering custom plugins manually...")
        relevant_yoe_plugin = RelevantYoEExtractorPlugin(llm_service=client._llm_service)
        education_stats_plugin = EducationStatsExtractorPlugin(llm_service=client._llm_service)
        work_stats_plugin = WorkStatsExtractorPlugin(llm_service=client._llm_service)
        social_plugin = SocialExtractorPlugin(llm_service=client._llm_service)
        
        # Add plugins directly to the plugin manager's plugins dictionary
        client._plugin_manager.plugins["relevant_yoe_extractor"] = relevant_yoe_plugin
        client._plugin_manager.plugins["education_stats_extractor"] = education_stats_plugin
        client._plugin_manager.plugins["work_stats_extractor"] = work_stats_plugin
        client._plugin_manager.plugins["social_extractor"] = social_plugin

        # Also add to extractors dictionary since they are ExtractorPlugins
        client._plugin_manager.extractors["relevant_yoe_extractor"] = relevant_yoe_plugin
        client._plugin_manager.extractors["education_stats_extractor"] = education_stats_plugin
        client._plugin_manager.extractors["work_stats_extractor"] = work_stats_plugin
        client._plugin_manager.extractors["social_extractor"] = social_plugin
        
        # Verify plugin registration
        print("\nVerifying plugin registration:")
        print(f"Total plugins: {len(client._plugin_manager.plugins)}")
        print(f"Total extractors: {len(client._plugin_manager.extractors)}")
        print("\nRegistered plugins:")
        for plugin_info in client._plugin_manager.list_plugins():
            print(f"- {plugin_info['name']} (v{plugin_info['version']}): {plugin_info['description']}")
        
        # Select a single resume file for testing
        test_file = "../Resumes/2023-08-28 - Wesley Ordonez Resume Wesley Ordonez 2023 (Data Analytics).pdf"
        
        print(f"\nTesting with resume: {test_file}")
        
        # Process the resume
        print("\nExtracting all information...")
        try:
            extraction_result = client.extract_all(test_file, log_token_usage=True)
            
            # Print the keys at the top level
            print("\nExtraction result structure:")
            print(f"Top-level keys: {list(extraction_result.keys())}")
            
            # Check if plugin_data exists
            if 'plugin_data' in extraction_result:
                print("\nFound plugin_data key!")
                plugin_data = extraction_result['plugin_data']
                print(f"Plugin data keys: {list(plugin_data.keys())}")
                
                # Check for our custom plugins
                custom_plugin_names = [
                    "relevant_yoe_extractor",
                    "education_stats_extractor",
                    "work_stats_extractor",
                    "social_extractor",
                ]
                
                for plugin_name in custom_plugin_names:
                    if plugin_name in plugin_data:
                        print(f"\nFound data for {plugin_name}:")
                        print(f"Type: {type(plugin_data[plugin_name])}")
                        pretty_print_dict(plugin_data[plugin_name])
                    else:
                        print(f"\nWarning: No data found for {plugin_name}")
                
                # Save the results to a JSON file for inspection
                with open('../Results/test_extraction_result.json', 'w') as f:
                    json.dump(extraction_result, f, indent=2)
                print("\nSaved extraction result to ../Results/test_extraction_result.json")
                
            else:
                print("\nWarning: No 'plugin_data' key found in extraction result!")
                print("Available keys:")
                for key in extraction_result:
                    value = extraction_result[key]
                    print(f"- {key} ({type(value)})")
                    if isinstance(value, dict) and len(value) < 10:
                        pretty_print_dict(value, indent=1)
            
        except Exception as e:
            print(f"Error extracting information: {str(e)}")
            traceback.print_exc()
        
    except Exception as e:
        print(f"Main error: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
