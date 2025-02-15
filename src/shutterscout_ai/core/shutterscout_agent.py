from loguru import logger
from smolagents import CodeAgent, HfApiModel

from shutterscout_ai.tools.combined.combiner import get_combined_data

INSTRUCTION_PROMPT = """You are ShutterScout AI, a photography location scout assistant. Make one call to
 get_combined_data() and analyze the results for photographers.

Analyze:
- Weather impact on photography (light, visibility, conditions)
- Best shooting times based on sun position and weather
- Location potential and current conditions
- Available sample photos

Format your response in markdown:

# 📍 ShutterScout.AI Location Overview
[Location and current conditions for photography]

## 🌤️ Photography Conditions
[Key weather factors affecting shoots]
- Temperature range
- Cloud cover impact
- Visibility conditions
- Wind considerations

## ⏰ Best Shooting Times
[Optimal times with reasoning]
- Sunrise/sunset timings
- Golden hour periods
- Weather-based recommendations

## 📸 Location Recommendations
[Top 3 locations with detailed photography tips]

### Location 1: [Name]
- **Best subjects/angles**: [Details]
- **Ideal timing**: [Time recommendations]
- **Technical tips**: [Camera settings, lens choices]
- **Unique features**: [Special photographic opportunities]

### Location 2: [Name]
- **Best subjects/angles**: [Details]
- **Ideal timing**: [Time recommendations]
- **Technical tips**: [Camera settings, lens choices]
- **Unique features**: [Special photographic opportunities]

### Location 3: [Name]
- **Best subjects/angles**: [Details]
- **Ideal timing**: [Time recommendations]
- **Technical tips**: [Camera settings, lens choices]
- **Unique features**: [Special photographic opportunities]

## 🎯 Sample Photos & Shot Ideas

### Available Photos
```markdown
[List of actual photos from photos_by_place with titles and URLs as markdown links]
- [Photo Title](URL)
```

### Recommended Shots
[For each location, at least one specific shot recommendation]
1. Location 1: [Specific shot idea with technical details]
2. Location 2: [Specific shot idea with technical details]
3. Location 3: [Specific shot idea with technical details]

## ⚠️ Photographer's Notes

### Equipment Needed
- [Comprehensive list of recommended equipment]
- [Specific gear for each location if needed]

### Access Information
- [Location access details for all 5 spots]
- [Opening hours and restrictions]
- [Parking information]

### Safety Considerations
- [Weather-related precautions]
- [Location-specific safety notes]
- [Equipment protection tips]"""


def create_shutterscout_agent(
    model_id: str = "meta-llama/Llama-3.3-70B-Instruct", temperature: float = 0.7, max_tokens: int = 2048
) -> CodeAgent:
    """
    Create and configure a ShutterScout AI agent with photography location scouting capabilities.

    Args:
        model_id: Hugging Face model identifier for the language model.
        temperature: Sampling temperature for model outputs (0.0-1.0).
        max_tokens: Maximum number of tokens in the model response.

    Returns:
        CodeAgent: Configured agent ready to provide photography location recommendations.
    """
    try:
        # Validate parameters
        if not (0.0 <= temperature <= 1.0):
            raise ValueError(f"Temperature must be between 0.0 and 1.0, got {temperature}")
        if max_tokens < 1:
            raise ValueError(f"max_tokens must be positive, got {max_tokens}")

        model = HfApiModel(model_id=model_id, temperature=temperature, max_tokens=max_tokens)

        agent = CodeAgent(tools=[get_combined_data], model=model, additional_authorized_imports=["json"])

        logger.info(f"Successfully created ShutterScout agent with model {model_id}")
        return agent

    except Exception as e:
        logger.error(f"Failed to create ShutterScout agent: {str(e)}")
        raise RuntimeError(f"Failed to create ShutterScout agent: {str(e)}") from e


def get_location_recommendations(custom_prompt: str = "", model_id: str = "meta-llama/Llama-3.3-70B-Instruct") -> str:
    """
    Generate photography location recommendations using the ShutterScout AI agent.
    Makes a single call to get_combined_data() to gather all necessary information.

    Args:
        custom_prompt: Optional custom instructions for analysis focus.
        model_id: Optional override for the model ID.
        latitude: Optional latitude coordinate for location override.
        longitude: Optional longitude coordinate for location override.

    Returns:
        str: Formatted recommendation text with practical photography guidance.
    """
    try:
        agent = create_shutterscout_agent(model_id=model_id)

        prompt = INSTRUCTION_PROMPT
        if custom_prompt:
            prompt += f"\n\nAdditional Focus:\n{custom_prompt}"

        result = agent.run(prompt)

        logger.info("Successfully generated location recommendations")
        return result

    except Exception as e:
        logger.error(f"Failed to get location recommendations: {str(e)}")
        raise RuntimeError(f"Failed to get location recommendations: {str(e)}") from e
