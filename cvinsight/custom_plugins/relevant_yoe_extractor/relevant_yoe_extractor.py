from typing import Dict, Any, Type, List, Optional, Tuple
from datetime import datetime

from pydantic import BaseModel, Field

from cvinsight.plugins.base import ExtractorPlugin, PluginMetadata, PluginCategory


class RelevantYearsOfExperience(BaseModel):
    """Relevant and all years of experience."""
    # Original fields (kept for backward compatibility)
    relevant_education_years: Optional[float] = Field(None, description="Number of years of RELEVANT education")
    relevant_job_experience_years: Optional[float] = Field(None, description="Number of years of RELEVANT job experience")
    total_relevant_experience_years: Optional[float] = Field(None, description="Total number of years of relevant experience (job + education)")
    
    # New fields with explicit naming
    relevant_edu_yoe: Optional[float] = Field(None, description="Number of years of RELEVANT education experience")
    all_edu_yoe: Optional[float] = Field(None, description="Number of years of ALL education experience")
    
    relevant_work_yoe: Optional[float] = Field(None, description="Number of years of RELEVANT work experience")
    all_work_yoe: Optional[float] = Field(None, description="Number of years of ALL work experience")
    
    relevant_total_yoe: Optional[float] = Field(None, description="Total number of years of RELEVANT experience (work + education)")
    all_total_yoe: Optional[float] = Field(None, description="Total number of years of ALL experience (work + education)")


class RelevantYoEExtractorPlugin(ExtractorPlugin):
    """Plugin to extract relevant years of experience."""

    def __init__(self, job_description: str = None, date_of_resume_submission: str = None, llm_service=None):
        """
        Initialize the plugin with optional job description and submission date.
        
        Args:
            job_description: Optional job description to determine relevance
            date_of_resume_submission: Date when the resume was submitted (for 'present' calculations)
            llm_service: LLM service for extraction
        """
        self.llm_service = llm_service
        self.job_description = job_description or """
        Looking for a Data Analyst with:
        - Experience in Python, SQL, and data visualization tools (Tableau, PowerBI)
        - Background in data cleaning, processing, and statistical analysis
        - Educational background in Statistics, Computer Science, Mathematics, or related field
        - Experience with data visualization and presenting insights to stakeholders
        - Familiarity with machine learning concepts is a plus
        """
        self.date_of_resume_submission = date_of_resume_submission

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="relevant_yoe_extractor",
            version="1.0.0",
            description="Extracts relevant years of education, job experience, and total relevant experience.",
            category=PluginCategory.CUSTOM,
            author="AI Assistant"
        )

    def initialize(self) -> None:
        pass

    def get_model(self) -> Type[BaseModel]:
        return RelevantYearsOfExperience

    def get_prompt_template(self) -> str:
        return """
        Analyze the following resume text to determine the candidate's years of experience, both RELEVANT to the job and ALL experience.
        Consider both education and job experience in relation to this job description:
        
        JOB DESCRIPTION:
        {job_description}
        
        TODAY'S DATE FOR CALCULATING PRESENT POSITIONS: {submission_date}
        
        Based on this job description and today's date:
        
        1. Education Experience:
           - Calculate the total years of ALL education (using the exact guidelines below)
           - Calculate the total years of RELEVANT education (education that directly applies to the job)
           
           Use the following EXACT guidelines for education years:
             - Diploma/certificate: 1 year (0.5 if pursuing)
             - Associate's degree: 2 years (1 if pursuing)
             - Bachelor's degree: 4 years (2 if pursuing)
             - Master's degree: 6 years (3 if pursuing)
             - PhD/Doctorate: 8 years (7 if pursuing)
             
        2. Work Experience:
           - Calculate the total years of ALL work experience (sum all positions)
           - Calculate the total years of RELEVANT work experience (work that directly applies to the job)
           
           For determining RELEVANCE in work experience:
             - Fully relevant: 100% of time counts (e.g., exact same role)
             - Highly relevant: ~75% of time counts (e.g., similar role with overlapping skills)
             - Moderately relevant: ~50% of time counts (e.g., different role but uses key required skills)
             - Slightly relevant: ~25% of time counts (e.g., different role with minimal relevant skills)
             - Not relevant: 0% of time counts (no overlap with required skills)
         
        3. Total Experience:
           - Calculate the total years of ALL experience (sum of ALL work + ALL education years)
           - Calculate the total years of RELEVANT experience (sum of RELEVANT work + RELEVANT education years)

        For positions listed as "present" or "current", calculate duration up to: {submission_date}
        Provide all output in numerical years with one decimal place precision (e.g., 2.5 for 2 years and 6 months).

        Resume Text:
        {text}

        {format_instructions}
        """

    def get_input_variables(self) -> List[str]:
        return ["text", "job_description", "submission_date"]
        
    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        # Use the current date if submission_date wasn't provided
        submission_date = self.date_of_resume_submission or datetime.now().strftime("%Y-%m-%d")
        
        return {
            "text": extracted_text,
            "job_description": self.job_description,
            "submission_date": submission_date
        }

    def map_degree_to_years(self, degree_info: Dict[str, Any]) -> float:
        """
        Map a degree to its corresponding education years, considering degree status.
        
        Args:
            degree_info: Dictionary containing degree information (highest_degree and highest_degree_status)
            
        Returns:
            Education years as a float
        """
        import logging
        
        if not degree_info or "highest_degree" not in degree_info:
            logging.warning("No highest_degree found in degree_info")
            return None
            
        highest_degree = degree_info.get("highest_degree", "").lower() if degree_info.get("highest_degree") else ""
        degree_status = degree_info.get("highest_degree_status", "").lower() if degree_info.get("highest_degree_status") else ""
        
        # Check if the degree is still being pursued (only counts for half)
        is_pursuing = degree_status == "pursuing"
        
        # Map degree levels to years based on status (pursuing/completed)
        # Following the requirements exactly with greatly expanded matching criteria:
        
        # Ph.D. / Doctorate level
        if any(phd_term in highest_degree for phd_term in [
            "phd", "doctorate", "doctor of", "ph.d", "ph d", "d.phil", "dphil", 
            "doctoral", "sc.d", "dr.", "doktor", "philosophy", "philosophiae"
        ]):
            logging.info(f"Detected PhD level degree: {highest_degree}")
            return 7.0 if is_pursuing else 8.0
            
        # Master's level - extensively expanded to include global variations
        elif any(masters_term in highest_degree for masters_term in [
            "master", "masters", "ms", "ma", "mba", "msc", "m.sc", "m.s.", "m.a.", "m.eng", "meng",
            "m.ed", "med", "m.phil", "mphil", "m.res", "mres", "m.st", "mst", "magister", 
            "m.arch", "march", "m.tech", "mtech", "llm", "ll.m", "macc", "m.acc", "mfin", "m.fin", 
            "mpa", "m.p.a", "mpp", "m.p.p", "msw", "m.s.w", "mls", "m.l.s", "msn", "m.s.n"
        ]):
            logging.info(f"Detected Master's level degree: {highest_degree}")
            return 3.0 if is_pursuing else 6.0
            
        # Bachelor's level - extensively expanded to include global variations
        elif any(bachelor_term in highest_degree for bachelor_term in [
            "bachelor", "bachelors", "bs", "ba", "bsc", "b.sc", "b.s.", "b.a.", "b.e.", "be", 
            "b.tech", "btech", "b.eng", "beng", "b.arch", "barch", "b.com", "bcom",
            "bfa", "b.f.a.", "b.b.a", "bba", "ll.b", "llb", "b.ed", "bed", "b.n", "bn", 
            "b.nurs", "b nursing", "bsn", "b.s.n", "bsw", "b.s.w", "undergraduate", 
            "laurea", "licenciatura", "bmus", "b.mus", "bsc hons", "b.sc. hons"
        ]):
            logging.info(f"Detected Bachelor's level degree: {highest_degree}")
            return 2.0 if is_pursuing else 4.0
            
        # Associate's level - expanded to include various formats
        elif any(associate_term in highest_degree for associate_term in [
            "associate", "associates", "associate's", "as", "aa", "a.s.", "a.a.", "a.a.s.", 
            "aas", "a.e.", "ae", "a.e.t", "aet", "a.b.a", "aba", "a.s.n", "asn",
            "foundation degree", "higher national diploma", "hnd", "two-year degree",
            "a.a.b", "aab", "a.g.s", "ags"
        ]):
            logging.info(f"Detected Associate's level degree: {highest_degree}")
            return 1.0 if is_pursuing else 2.0
            
        # Diploma/Certificate level - expanded to include various formats
        elif any(diploma_term in highest_degree for diploma_term in [
            "diploma", "certificate", "online", "certification", "cert", "bootcamp", 
            "professional certification", "prof cert", "nanodegree", "microdegree",
            "post-graduate diploma", "post graduate diploma", "pgd", "p.g.d.", "short course",
            "graduate diploma", "grad diploma", "grad dip", "grad.dip.", "technical diploma",
            "vocational certificate", "apprenticeship", "trade certificate", "tech cert"
        ]):
            logging.info(f"Detected Diploma/Certificate level: {highest_degree}")
            return 0.5 if is_pursuing else 1.0
            
        # If no specific degree type is found, try to determine from the context
        else:
            # Log detailed warning for debugging
            logging.warning(f"Attempting to infer degree type from context: '{highest_degree}', status: '{degree_status}'")
            
            # Special case for "engineering" degrees that might be bachelor's
            if "engineer" in highest_degree and not any(higher_term in highest_degree for higher_term in ["master", "phd", "doctor"]):
                logging.info(f"Inferred Bachelor's level engineering degree from: {highest_degree}")
                return 2.0 if is_pursuing else 4.0
                
            # If still can't determine, default conservative values
            logging.warning(f"Could not determine education years for degree: {highest_degree}, status: {degree_status}")
            return 0.5 if is_pursuing else 1.0
            
    def process_output(self, result: Any, education_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process the output from the LLM extraction and apply corrections based on our degree-to-years mapping.
        
        Args:
            result: The LLM extraction result
            education_info: Optional education info from education_stats_extractor
            
        Returns:
            Processed output with corrected education years
        """
        import logging
        
        if isinstance(result, RelevantYearsOfExperience):
            result_dict = result.model_dump()
        else:
            result_dict = result
        
        # Create a mapping from old field names to new field names
        field_mapping = {
            "relevant_education_years": "relevant_edu_yoe",
            "relevant_job_experience_years": "relevant_work_yoe",
            "total_relevant_experience_years": "relevant_total_yoe"
        }
        
        # Ensure all values are present in both old and new fields
        for old_name, new_name in field_mapping.items():
            # If only old name has value, copy to new name
            if result_dict.get(old_name) is not None and result_dict.get(new_name) is None:
                result_dict[new_name] = result_dict[old_name]
            # If only new name has value, copy to old name
            elif result_dict.get(new_name) is not None and result_dict.get(old_name) is None:
                result_dict[old_name] = result_dict[new_name]
            
        # If we have education_info and the degree can be determined
        if education_info:
            mapped_years = self.map_degree_to_years(education_info)
            
            # Only override if we got a valid mapping and either:
            # 1. The LLM didn't provide a value (None)
            # 2. The LLM's value is significantly different from our mapping (20% tolerance)
            current_years = result_dict.get("relevant_edu_yoe") or result_dict.get("relevant_education_years")
            all_edu_years = result_dict.get("all_edu_yoe")
            
            if mapped_years is not None:
                # Log detailed information about the degree mapping
                logging.info(f"Degree mapping details:")
                logging.info(f"- Highest degree: {education_info.get('highest_degree', 'Unknown')}")
                logging.info(f"- Degree status: {education_info.get('highest_degree_status', 'Unknown')}")
                logging.info(f"- Mapped years: {mapped_years}")
                logging.info(f"- Original LLM education years (relevant): {current_years}")
                logging.info(f"- Original LLM education years (all): {all_edu_years}")
                
                # If all_edu_yoe is not set, use the mapped years
                if all_edu_years is None:
                    logging.info(f"Setting all education years to {mapped_years} based on degree mapping")
                    result_dict["all_edu_yoe"] = mapped_years
                
                # For relevant education, only set if it's missing or significantly different
                if current_years is None:
                    # Use the same mapped value for both fields for backward compatibility
                    logging.info(f"Setting relevant education years to {mapped_years} based on degree mapping")
                    result_dict["relevant_education_years"] = mapped_years
                    result_dict["relevant_edu_yoe"] = mapped_years
                elif abs(current_years - mapped_years) > (mapped_years * 0.2):  # 20% tolerance
                    logging.info(f"Correcting education years from {current_years} to {mapped_years} based on degree mapping")
                    result_dict["relevant_education_years"] = mapped_years
                    result_dict["relevant_edu_yoe"] = mapped_years
        
        # Calculate totals for all experience metrics (both relevant and all)            
        # Calculate total relevant experience
        if (result_dict.get("relevant_edu_yoe") is not None or result_dict.get("relevant_education_years") is not None) and \
           (result_dict.get("relevant_work_yoe") is not None or result_dict.get("relevant_job_experience_years") is not None):
            
            edu_yoe = result_dict.get("relevant_edu_yoe") or result_dict.get("relevant_education_years", 0)
            work_yoe = result_dict.get("relevant_work_yoe") or result_dict.get("relevant_job_experience_years", 0)
            
            calculated_total = edu_yoe + work_yoe
            
            # Update both fields
            result_dict["relevant_total_yoe"] = calculated_total
            result_dict["total_relevant_experience_years"] = calculated_total
        
        # Calculate total all experience
        if result_dict.get("all_edu_yoe") is not None and result_dict.get("all_work_yoe") is not None:
            result_dict["all_total_yoe"] = result_dict["all_edu_yoe"] + result_dict["all_work_yoe"]
                
        return result_dict
        
    def extract(self, text: str, education_stats: Dict[str, Any] = None, additional_params: Dict[str, Any] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extract relevant years of experience information from text.
        
        Args:
            text: The text to extract information from.
            education_stats: Optional education stats from education_stats_extractor
            additional_params: Optional additional parameters like date_of_resume_submission or job_description
            
        Returns:
            A tuple of (extracted_data, token_usage)
        """
        import logging
        
        # Log whether we received education stats
        if education_stats:
            logging.info(f"Received education stats with keys: {education_stats.keys()}")
        else:
            logging.warning("No education stats provided to relevant_yoe_extractor")
        
        # Set temporary job_description and date_of_resume_submission if provided in additional_params
        original_job_description = self.job_description
        original_date = self.date_of_resume_submission
        
        if additional_params:
            logging.info(f"Received additional parameters: {additional_params.keys()}")
            if additional_params.get("job_description"):
                self.job_description = additional_params["job_description"]
                logging.info(f"Using job description from additional parameters")
            if additional_params.get("date_of_resume_submission"):
                self.date_of_resume_submission = additional_params["date_of_resume_submission"]
                logging.info(f"Using submission date from additional parameters: {self.date_of_resume_submission}")
        
        # Prepare prompt from template
        prompt_template = self.get_prompt_template()
        input_data = self.prepare_input_data(text)
        input_variables = self.get_input_variables()
        model = self.get_model()
        
        try:
            # Call LLM service
            result, token_usage = self.llm_service.extract_with_llm(
                model,
                prompt_template,
                input_variables,
                input_data
            )
            
            # Add extractor name to token usage
            token_usage["extractor"] = self.metadata.name
            
            # Log the raw LLM result
            logging.info(f"Raw LLM result for relevant YoE: {result}")
            
            # Process the result using the process_output method
            processed_result = self.process_output(result, education_stats)
            
            # Log the extracted result
            logging.info(f"Extracted relevant YoE: {processed_result}")
            
            return processed_result, token_usage
            
        finally:
            # Restore original values
            self.job_description = original_job_description
            self.date_of_resume_submission = original_date
