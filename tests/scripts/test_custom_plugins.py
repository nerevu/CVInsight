"""
Direct testing script for custom plugins in the CVInsight system.
This script directly uses the custom plugins to extract information from a single resume.
"""
import os
import sys
import traceback

# Add the project root to sys.path when running as a script
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

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
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            api_key = os.environ.get("OPEN_AI_API_KEY")
            if not api_key:
                raise ValueError("No API key found in environment variables")
        
        # Initialize the CVInsight client
        client = CVInsightClient(
            api_key=api_key,
            provider="openai",  # Use OpenAI by default
            model_name="o4-mini-2025-04-16"  # Use o4-mini model
        )
        
        # Create instances of our custom plugins
        relevant_yoe_plugin = RelevantYoEExtractorPlugin(llm_service=client._llm_service)
        education_stats_plugin = EducationStatsExtractorPlugin(llm_service=client._llm_service)
        work_stats_plugin = WorkStatsExtractorPlugin(llm_service=client._llm_service)
        social_plugin = SocialExtractorPlugin(llm_service=client._llm_service)
        
        # Register the plugins with the client
        client._plugin_manager.plugins["relevant_yoe_extractor"] = relevant_yoe_plugin
        client._plugin_manager.plugins["education_stats_extractor"] = education_stats_plugin
        client._plugin_manager.plugins["work_stats_extractor"] = work_stats_plugin
        client._plugin_manager.plugins["social_extractor"] = social_plugin
        
        # Also add to extractors dictionary
        client._plugin_manager.extractors["relevant_yoe_extractor"] = relevant_yoe_plugin
        client._plugin_manager.extractors["education_stats_extractor"] = education_stats_plugin
        client._plugin_manager.extractors["work_stats_extractor"] = work_stats_plugin
        client._plugin_manager.extractors["social_extractor"] = social_plugin
        
        # Print registered plugins
        print("\nRegistered plugins:")
        for plugin_info in client._plugin_manager.list_plugins():
            print(f"- {plugin_info['name']} (v{plugin_info['version']}): {plugin_info['description']}")
        
        # Set the test resume path (use the first resume in the Resumes folder)
        resume_paths = [
            os.path.join("Resumes", resume_file) 
            for resume_file in os.listdir("Resumes") 
            if resume_file.endswith(('.pdf', '.docx', '.doc'))
        ]
        if not resume_paths:
            raise ValueError("No resume files found in the Resumes directory")
        
        test_resume_path = resume_paths[0]
        print(f"\nTesting with resume: {test_resume_path}")
        
        # Extract text from the resume
        extracted_text = client._processor._extract_text_from_file(test_resume_path)
        
        # Test with profile extractor
        print("\nTesting profile extractor:")
        profile_result, _ = client._plugin_manager.extractors['profile_extractor'].extract(extracted_text)
        print(f"Profile result: {profile_result}")
        
        # Test with education extractor
        print("\nTesting education extractor:")
        education_result, _ = client._plugin_manager.extractors['education_extractor'].extract(extracted_text)
        print(f"Education result: {education_result}")
        
        # Test with experience extractor
        print("\nTesting experience extractor:")
        experience_result, _ = client._plugin_manager.extractors['experience_extractor'].extract(extracted_text)
        print(f"Experience result: {experience_result}")
        
        # Test with education_stats_extractor
        print("\nTesting education stats extractor:")
        education_stats_result, _ = client._plugin_manager.extractors['education_stats_extractor'].extract(education_result)
        print(f"Education stats result: {education_stats_result}")
        
        # Test with work_stats_extractor
        print("\nTesting work stats extractor:")
        work_stats_result, _ = client._plugin_manager.extractors['work_stats_extractor'].extract(experience_result)
        print(f"Work stats result: {work_stats_result}")
        
        # Test with social_extractor
        print("\nTesting social extractor:")
        social_result, _ = client._plugin_manager.extractors['social_extractor'].extract(extracted_text)
        print(f"Social result: {social_result}")
        
        # Test with relevant_yoe_extractor
        print("\nTesting relevant YoE extractor:")
        relevant_yoe_result, _ = client._plugin_manager.extractors['relevant_yoe_extractor'].extract(
            extracted_text, education_stats_result
        )
        print(f"Relevant YoE result: {relevant_yoe_result}")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
