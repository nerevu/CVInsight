"""Unit tests for base plugin functionality."""
import pytest
from unittest.mock import MagicMock, patch
from cvinsight.plugins.base import BasePlugin, ExtractorPlugin, PluginMetadata, PluginCategory

class TestBasePlugin(BasePlugin):
    """Test implementation of BasePlugin."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            category=PluginCategory.BASE,
            author="Test Author"
        )
    
    def initialize(self) -> None:
        """Initialize the plugin."""
        pass

class TestExtractorPlugin(ExtractorPlugin):
    """Test implementation of ExtractorPlugin."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="test_extractor",
            version="1.0.0",
            description="Test extractor",
            category=PluginCategory.BASE,
            author="Test Author"
        )
    
    def initialize(self) -> None:
        """Initialize the plugin."""
        pass
    
    def get_model(self):
        """Get the model for the extractor."""
        return None
    
    def get_prompt_template(self) -> str:
        """Get the prompt template."""
        return "test template"
    
    def get_input_variables(self) -> list:
        """Get input variables."""
        return ["test_var"]
    
    def prepare_input_data(self, extracted_text: str) -> dict:
        """Prepare input data."""
        return {"test_var": extracted_text}
    
    def extract(self, extracted_text: str) -> tuple:
        """Extract data."""
        return {"test": "data"}, None

def test_base_plugin_initialization():
    """Test base plugin initialization."""
    plugin = TestBasePlugin()
    assert plugin.metadata.name == "test_plugin"
    assert plugin.metadata.version == "1.0.0"
    assert plugin.metadata.description == "Test plugin"
    assert plugin.metadata.category == PluginCategory.BASE
    assert plugin.metadata.author == "Test Author"

def test_base_plugin_initialize():
    """Test base plugin initialize method."""
    plugin = TestBasePlugin()
    # Should not raise any exception
    plugin.initialize()

def test_extractor_plugin_initialization():
    """Test extractor plugin initialization."""
    plugin = TestExtractorPlugin()
    assert plugin.metadata.name == "test_extractor"
    assert plugin.metadata.version == "1.0.0"
    assert plugin.metadata.description == "Test extractor"
    assert plugin.metadata.category == PluginCategory.BASE
    assert plugin.metadata.author == "Test Author"

def test_extractor_plugin_methods():
    """Test extractor plugin methods."""
    plugin = TestExtractorPlugin()
    
    # Test get_model
    assert plugin.get_model() is None
    
    # Test get_prompt_template
    assert plugin.get_prompt_template() == "test template"
    
    # Test get_input_variables
    assert plugin.get_input_variables() == ["test_var"]
    
    # Test prepare_input_data
    input_data = plugin.prepare_input_data("test text")
    assert input_data == {"test_var": "test text"}
    
    # Test extract
    result, token_usage = plugin.extract("test text")
    assert result == {"test": "data"}
    assert token_usage is None

def test_extractor_plugin_initialize():
    """Test extractor plugin initialize method."""
    plugin = TestExtractorPlugin()
    # Should not raise any exception
    plugin.initialize() 