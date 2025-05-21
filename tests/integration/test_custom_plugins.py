"""
Direct testing script for custom plugins in the CVInsight system.
This script directly uses the custom plugins to extract information from a single resume.
"""
import os
import sys
import traceback

# Add the project root to the Python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cvinsight import CVInsightClient
from cvinsight.custom_plugins import (
    RelevantYoEExtractorPlugin,
    EducationStatsExtractorPlugin,
    WorkStatsExtractorPlugin,
    SocialExtractorPlugin
)
from dotenv import load_dotenv

def main():
    try:
        # Load environment variables and get API key
        load_dotenv()
        # Use OpenAI API key instead of Gemini
        api_key = os.environ.get("OPEN_AI_API_KEY")
        
        if not api_key:
            print("Error: OPEN_AI_API_KEY environment variable not found")
            return
            
        print(f"API Key found: {api_key[:5]}...")
        
        # Initialize the CVInsight client with OpenAI
        print("Initializing CVInsight client...")
        client = CVInsightClient(
            api_key=api_key, 
            provider="openai",
            model_name="o4-mini-2025-04-16"
        )
        
        # Create Results directory if it doesn't exist
        if not os.path.exists("../Results"):
            os.makedirs("../Results")
            print("Created Results directory")
        
        # Select a single resume file for testing
        test_file = "../Resumes/2023-08-28 - Wesley Ordonez Resume Wesley Ordonez 2023 (Data Analytics).pdf"
        
        print(f"Testing custom plugins with resume: {test_file}")
        
        # Extract basic information using the built-in plugins first
        print("\nExtracting text from file...")
        try:
            extracted_text = client._processor._extract_text_from_file(test_file)
            print(f"Extracted text length: {len(extracted_text)}")
        except Exception as e:
            print(f"Error extracting text: {str(e)}")
            traceback.print_exc()
            return
        
        if not extracted_text:
            print("Failed to extract text from file")
            return
        
        # Create instances of our custom plugins
        print("\nCreating plugin instances...")
        
        try:
            relevant_yoe_plugin = RelevantYoEExtractorPlugin(llm_service=client._llm_service)
            print("Created RelevantYoEExtractorPlugin")
        except Exception as e:
            print(f"Error creating RelevantYoEExtractorPlugin: {str(e)}")
            traceback.print_exc()
        
        try:
            education_stats_plugin = EducationStatsExtractorPlugin(llm_service=client._llm_service)
            print("Created EducationStatsExtractorPlugin")
        except Exception as e:
            print(f"Error creating EducationStatsExtractorPlugin: {str(e)}")
            traceback.print_exc()
        
        try:
            work_stats_plugin = WorkStatsExtractorPlugin(llm_service=client._llm_service)
            print("Created WorkStatsExtractorPlugin")
        except Exception as e:
            print(f"Error creating WorkStatsExtractorPlugin: {str(e)}")
            traceback.print_exc()
        
        try:
            social_plugin = SocialExtractorPlugin(llm_service=client._llm_service)
            print("Created SocialExtractorPlugin")
        except Exception as e:
            print(f"Error creating SocialExtractorPlugin: {str(e)}")
            traceback.print_exc()
        
        # Directly call each plugin's extract method
        print("\nTesting RelevantYoEExtractorPlugin:")
        try:
            relevant_yoe_result, _ = relevant_yoe_plugin.extract(extracted_text)
            print(f"Result type: {type(relevant_yoe_result)}")
            print(f"Result: {relevant_yoe_result}")
            
            # Check if result can be properly stored in Resume object
            test_resume = {"plugin_data": {}}
            test_resume["plugin_data"][relevant_yoe_plugin.metadata.name] = relevant_yoe_result
            print(f"Test Resume plugin_data structure: {test_resume['plugin_data']}")
        except Exception as e:
            print(f"Error using RelevantYoEExtractorPlugin: {str(e)}")
            traceback.print_exc()
        
        print("\nTesting EducationStatsExtractorPlugin:")
        try:
            education_stats_result, _ = education_stats_plugin.extract(extracted_text)
            print(f"Result type: {type(education_stats_result)}")
            print(f"Result: {education_stats_result}")
            
            # Check if result can be properly stored in Resume object
            test_resume = {"plugin_data": {}}
            test_resume["plugin_data"][education_stats_plugin.metadata.name] = education_stats_result
            print(f"Test Resume plugin_data structure: {test_resume['plugin_data']}")
        except Exception as e:
            print(f"Error using EducationStatsExtractorPlugin: {str(e)}")
            traceback.print_exc()
        
        print("\nTesting WorkStatsExtractorPlugin:")
        try:
            work_stats_result, _ = work_stats_plugin.extract(extracted_text)
            print(f"Result type: {type(work_stats_result)}")
            print(f"Result: {work_stats_result}")
            
            # Check if result can be properly stored in Resume object
            test_resume = {"plugin_data": {}}
            test_resume["plugin_data"][work_stats_plugin.metadata.name] = work_stats_result
            print(f"Test Resume plugin_data structure: {test_resume['plugin_data']}")
        except Exception as e:
            print(f"Error using WorkStatsExtractorPlugin: {str(e)}")
            traceback.print_exc()
        
        print("\nTesting SocialExtractorPlugin:")
        try:
            social_result, _ = social_plugin.extract(extracted_text)
            print(f"Result type: {type(social_result)}")
            print(f"Result: {social_result}")
            
            # Check if result can be properly stored in Resume object
            test_resume = {"plugin_data": {}}
            test_resume["plugin_data"][social_plugin.metadata.name] = social_result
            print(f"Test Resume plugin_data structure: {test_resume['plugin_data']}")
        except Exception as e:
            print(f"Error using SocialExtractorPlugin: {str(e)}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"Main error: {str(e)}")
        traceback.print_exc()
    
if __name__ == "__main__":
    main()
