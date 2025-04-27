# Centralized Model Definitions

This directory contains the centralized model definitions for the Imagi Oasis platform. The `model_definitions.py` file serves as the single source of truth for all AI model information across both the backend and frontend.

## Key Features

1. **Single Source of Truth**: All model information including IDs, names, costs, capabilities, and API versions are defined in one place.

2. **Consistent API Access**: Helper functions provide consistent access to model data across the codebase.

3. **Frontend Integration**: Model definitions are exposed via a REST API to ensure frontend and backend stay in sync.

## Usage

### Backend Usage

Import the necessary functions from the module:

```python
from apps.Products.Oasis.Agents.services.model_definitions import (
    get_model_choices,
    get_provider_choices,
    get_model_cost,
    get_model_by_id,
    # etc.
)
```

For Django models:

```python
model_name = models.CharField(max_length=50, choices=get_model_choices())
provider = models.CharField(max_length=20, choices=get_provider_choices(), default=get_default_provider())
```

For service layer logic:

```python
# Get a specific model definition
model_def = get_model_by_id(model_id)

# Get the cost for a model
cost = get_model_cost(model_id)

# Get the provider for a model
provider = get_provider_from_model_id(model_id)

# Get the API version for a model
api_version = get_api_version_from_model_id(model_id)
```

### Adding New Models

When adding a new model:

1. Add the model definition to the `MODELS` dictionary in `model_definitions.py`
2. Add pricing information if relevant
3. Specify the API version ('chat', 'messages', 'responses')

No other code changes are needed for the model to be available throughout the system.

### Frontend Integration

The frontend fetches model definitions from the `/api/v1/agents/models/` endpoint, ensuring it stays in sync with backend definitions.

## Best Practices

- Always reference model_definitions.py for model information
- Never hardcode model IDs, names, or other data
- Use the provided helper functions to access model information
- When adding new models, only update the MODELS dictionary 