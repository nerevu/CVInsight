# Technical Documentation

This page provides detailed technical documentation about the internal implementation of the CVInsight package.

## Core Components

### CVInsightClient

The main client interface for interacting with the CVInsight package.

```python
class CVInsightClient:
    """Client for CVInsight resume analysis."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """Initialize the CVInsight client."""
        # Store API key in environment if provided
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
            
        # Initialize services
        self._llm_service = LLMService(model_name=model_name)
        self._plugin_manager = PluginManager(self._llm_service)
        self._plugin_manager.load_all_plugins()
        self._processor = ResumeProcessor(plugin_manager=self._plugin_manager)
    
    def extract_all(self, file_path: str, log_token_usage: bool = True) -> Dict[str, Any]:
        """Extract all information from a resume."""
        pass
        
    def extract_profile(self, file_path: str) -> Dict[str, Any]:
        """Extract profile information from a resume."""
        pass
        
    def extract_education(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract education information from a resume."""
        pass
        
    def extract_experience(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract experience information from a resume."""
        pass
        
    def extract_skills(self, file_path: str) -> Dict[str, Any]:
        """Extract skills information from a resume."""
        pass
        
    def extract_years_of_experience(self, file_path: str) -> Optional[str]:
        """Extract years of experience from a resume."""
        pass
        
    def analyze_resume(self, resume_path: Union[str, pathlib.Path], 
                      plugins: Optional[List[str]] = None,
                      log_token_usage: bool = True) -> Dict[str, Any]:
        """Analyze a resume using specific plugins."""
        pass
        
    def list_all_plugins(self) -> List[Dict[str, Any]]:
        """List all available plugins."""
        pass
        
    def list_plugins_by_category(self, category: str) -> List[Dict[str, Any]]:
        """List plugins by category."""
        pass
```

### BasePlugin

The abstract base class for all plugins.

```python
class BasePlugin(ABC):
    """Abstract base class for all CVInsight plugins."""
    
    def __init__(self, llm_service: LLMService):
        """Initialize the plugin with a language model service."""
        self.llm_service = llm_service
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Get the metadata of the plugin."""
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the plugin."""
        pass
    
    @abstractmethod
    def get_model(self) -> Type[BaseModel]:
        """Get the Pydantic model for the plugin."""
        pass
    
    @abstractmethod
    def get_prompt_template(self) -> str:
        """Get the prompt template for the plugin."""
        pass
    
    @abstractmethod
    def get_input_variables(self) -> List[str]:
        """Get the input variables for the prompt template."""
        pass
    
    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        """Prepare input data for the prompt template."""
        return {"text": extracted_text}
    
    def extract(self, extracted_text: str) -> Tuple[Dict[str, Any], Optional[Dict[str, int]]]:
        """Extract information from text."""
        pass
```

### ExtractorPlugin

The base class for extractor plugins.

```python
class ExtractorPlugin(BasePlugin):
    """Base class for all extractor plugins."""
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Get the metadata of the plugin."""
        pass
    
    def extract(self, text: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Extract information from text."""
        # Prepare prompt from template
        prompt_template = self.get_prompt_template()
        input_data = self.prepare_input_data(text)
        input_variables = self.get_input_variables()
        model = self.get_model()
        
        # Call LLM service
        result, token_usage = self.llm_service.extract_with_llm(
            model,
            prompt_template,
            input_variables,
            input_data
        )
        
        # Add extractor name to token usage
        token_usage["extractor"] = self.metadata.name
        
        # Process and return the result
        processed_result = self.process_output(result)
        
        return processed_result, token_usage
        
    def process_output(self, result: Any) -> Dict[str, Any]:
        """Process the output from the LLM."""
        pass
```

### PluginManager

Manages plugin discovery, loading, and access.

```python
class PluginManager:
    """Manager for CVInsight plugins."""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """Initialize the plugin manager."""
        self.llm_service = llm_service
        self.plugins: Dict[str, BasePlugin] = {}
        
    def load_all_plugins(self) -> Dict[str, BasePlugin]:
        """Load all available plugins."""
        pass
        
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get a plugin by name."""
        return self.plugins.get(name)
        
    def get_plugins_by_category(self, category: str) -> Dict[str, BasePlugin]:
        """Get all plugins in a category."""
        return {name: plugin for name, plugin in self.plugins.items() 
                if plugin.metadata.category == category}
                
    def get_extractor_plugins(self) -> Dict[str, ExtractorPlugin]:
        """Get all extractor plugins."""
        return {name: plugin for name, plugin in self.plugins.items() 
                if isinstance(plugin, ExtractorPlugin)}
                
    def register_plugin(self, plugin: BasePlugin) -> None:
        """Register a new plugin."""
        self.plugins[plugin.metadata.name] = plugin
```

### PluginResumeProcessor

Processes resumes using the plugin system.

```python
class PluginResumeProcessor:
    """Class for processing resumes using the plugin system."""
    
    def __init__(self, resume_dir: str = "./Resumes", output_dir: str = "./Results", 
                 log_dir: str = "./logs/token_usage", plugin_manager: Optional[Any] = None):
        """Initialize the PluginResumeProcessor."""
        self.resume_dir = resume_dir
        self.output_dir = output_dir
        self.log_dir = log_dir
        self.plugin_manager = plugin_manager
        
        # Ensure output directories exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
    
    def process_resume(self, pdf_file_path: str) -> Optional[Resume]:
        """Process a single resume file using plugins."""
        pass
        
    def process_all_resumes(self) -> Tuple[int, int]:
        """Process all resumes in the resume directory."""
        pass
        
    def save_resume(self, resume: Resume) -> None:
        """Save a processed resume to the output directory."""
        pass
        
    def print_token_usage_report(self, resume: Resume, log_file: str = None) -> None:
        """Print a report of token usage for a resume."""
        pass
```

### LLMService

Centralized service for interacting with language models.

```python
class LLMService:
    """Service for interacting with LLM API."""
    
    def __init__(self, model_name=None, api_key=None):
        """Initialize the LLM service."""
        self.model_name = model_name or config.DEFAULT_LLM_MODEL
        self.api_key = api_key or config.GOOGLE_API_KEY or os.environ.get("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("Google API key is required.")
            
        self.llm = self._get_llm()
    
    def _get_llm(self):
        """Get a LLM instance."""
        return ChatGoogleGenerativeAI(api_key=self.api_key, model=self.model_name)
    
    def create_extraction_chain(self, pydantic_model: Type[BaseModel], prompt_template: str, input_variables: list):
        """Create a chain for extracting information using a language model."""
        pass
    
    def extract_with_llm(self, pydantic_model: Type[BaseModel], prompt_template: str, 
                        input_variables: list, input_data: dict) -> Tuple[Any, Dict[str, int]]:
        """Extract information from text using a language model."""
        pass
```

## Data Models

### PluginMetadata

```python
class PluginMetadata:
    """Metadata for a plugin."""
    name: str           # Unique identifier for the plugin
    version: str        # Version number (semantic versioning recommended)
    description: str    # Brief description of what the plugin does
    category: str       # Plugin category (use PluginCategory enum)
    author: str         # Plugin author name
```

### PluginCategory

```python
class PluginCategory:
    """Categories for plugins."""
    BASE = "BASE"           # Core functionality
    EXTRACTOR = "EXTRACTOR" # Data extraction
    PROCESSOR = "PROCESSOR" # Data processing
    ANALYZER = "ANALYZER"   # Data analysis
    CUSTOM = "CUSTOM"       # Custom functionality
    UTILITY = "UTILITY"     # Utility functions
```

### Resume

The main data model for storing resume information.

```python
class Resume(BaseModel):
    """A complete resume with all extracted information."""
    file_path: Optional[str] = None
    name: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    educations: List[Education] = Field(default_factory=list)
    work_experiences: List[WorkExperience] = Field(default_factory=list)
    YoE: Optional[str] = None
    token_usage: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_extractors_output(cls, profile, skills, education, experience, yoe, file_path=None, token_usage=None):
        """Create a Resume object from the output of various extractors."""
        pass
        
    def add_plugin_data(self, plugin_name: str, data: Any) -> None:
        """Add custom plugin data to the resume."""
        pass
```

### Other Models

```python
class ResumeProfile(BaseModel):
    """Profile information from a resume."""
    name: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[str] = None

class Education(BaseModel):
    """Educational information from a resume."""
    institution: str
    degree: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None

class WorkExperience(BaseModel):
    """Work experience information from a resume."""
    company: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

class Skills(BaseModel):
    """Skills information from a resume."""
    skills: List[str] = Field(default_factory=list)

class YearsOfExperience(BaseModel):
    """Years of experience information from a resume."""
    YoE: str
```

## Utility Functions

### File Reading

```python
def read_file(file_path: str) -> str:
    """Read and extract text from a file."""
    # Validate the file
    is_valid, message = validate_file(file_path)
    if not is_valid:
        raise ValueError(f"Invalid file: {message}")
    
    # Get the file extension
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Extract text based on file extension
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")
```

### Token Usage Tracking

```python
class TokenUsageCallbackHandler(BaseCallbackHandler):
    """Callback handler for tracking token usage."""
    
    def __init__(self):
        """Initialize the callback handler."""
        super().__init__()
        self.token_usage = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "source": "not_set"
        }
        
    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Extract token usage from the LLM response."""
        pass
```

## CLI Interface

```python
@click.command(help="CVInsight - AI-powered resume analysis")
@click.option('--resume', type=str, help='Process a single resume file')
@click.option('--output', type=str, help='Output directory for results')
@click.option('--list-plugins', is_flag=True, help='List available plugins')
@click.option('--plugins', type=str, help='Comma-separated list of plugins to use')
@click.option('--json', 'json_output', is_flag=True, help='Output results as JSON')
def main(resume: Optional[str], output: Optional[str], list_plugins: bool, plugins: Optional[str], json_output: bool):
    """Entry point for the CVInsight CLI."""
    pass
```

## Package Structure

```
cvinsight/
├── __init__.py                  # Package exports
├── client.py                    # CVInsightClient implementation
├── api.py                       # Functional API
├── cli.py                       # Command-line interface
├── base_plugins/                # Base plugins
│   ├── __init__.py
│   ├── base.py                  # Abstract base classes
│   ├── plugin_manager.py        # Plugin manager
│   ├── profile_extractor/       # Profile extractor plugin
│   ├── skills_extractor/        # Skills extractor plugin
│   ├── education_extractor/     # Education extractor plugin
│   ├── experience_extractor/    # Experience extractor plugin
│   └── yoe_extractor/           # YoE extractor plugin
├── core/                        # Core functionality
│   ├── __init__.py
│   ├── config.py                # Configuration settings
│   ├── constants.py             # Constants
│   ├── llm_service.py           # LLM service
│   ├── resume_processor.py      # Resume processor
│   └── utils/                   # Utility functions
├── models/                      # Data models
│   ├── __init__.py
│   └── resume_models.py         # Resume-related models
├── plugins/                     # Plugin system
│   ├── __init__.py
│   └── base.py                  # Plugin interfaces
└── custom_plugins/              # Custom plugins directory
    └── __init__.py
``` 