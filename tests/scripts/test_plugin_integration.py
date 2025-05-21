#!/usr/bin/env python3
"""
This script tests the integration of custom plugins with the CVInsight client.
It focuses on ensuring that custom plugin data is correctly extracted and accessible.
"""
import os
import sys
import json
import traceback

# Add the project root to sys.path when running as a script
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

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
    """
    Print dictionary with indentation for better readability.
    """
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{'  ' * indent}{key}:")
            pretty_print_dict(value, indent + 1)
        elif isinstance(value, list):
            print(f"{'  ' * indent}{key}: [list with {len(value)} items]")
        else:
            print(f"{'  ' * indent}{key}: {value}")

def main():
    try:
        # Load environment variables
        load_dotenv()
        
        # Get API key from environment
        api_key = os.environ.get("OPEN_AI_API_KEY")
        if not api_key:
            raise ValueError("OPEN_AI_API_KEY is not set in the .env file")
            
        # Initialize the CVInsight client
        client = CVInsightClient(
            api_key=api_key,
            provider="openai",  # Specify to use OpenAI
            model_name="o4-mini-2025-04-16"  # Use o4-mini model
        )
        
        # Register our custom plugins with the client
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
        
        # Print registered plugins
        print("\nRegistered plugins:")
        for plugin_info in client._plugin_manager.list_plugins():
            print(f"- {plugin_info['name']} (v{plugin_info['version']}): {plugin_info['description']}")
            
        # Find resume files
        resume_paths = [
            os.path.join("Resumes", f) 
            for f in os.listdir("Resumes") 
            if f.lower().endswith(('.pdf', '.docx', '.doc'))
        ]
        
        if not resume_paths:
            raise ValueError("No resume files found in Resumes directory")
            
        # Use the first resume file for testing
        resume_path = resume_paths[0]
        print(f"\nTesting with resume: {resume_path}")
        
        # Extract all information from the resume
        result = client.extract_all(resume_path)
        
        # Check for the plugin_data key
        if 'plugin_data' not in result:
            print("\nWARNING: No plugin_data found in extraction result.")
            print("Available keys:", result.keys())
        else:
            print("\nPlugin data found in extraction result!")
            plugin_data = result['plugin_data']
            print(f"Plugin data keys: {plugin_data.keys()}")
            
            # Check for each of our custom plugins
            for plugin_name in ["relevant_yoe_extractor", "education_stats_extractor", "work_stats_extractor", "social_extractor"]:
                if plugin_name in plugin_data:
                    print(f"\n{plugin_name} data found:")
                    pretty_print_dict(plugin_data[plugin_name])
                else:
                    print(f"\nWARNING: {plugin_name} data not found in plugin_data.")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
