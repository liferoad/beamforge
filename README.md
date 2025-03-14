# beamforge

## Description

A Dash app for visually building and managing Beam pipelines using Beam YAML.

## About

This is a side project to explore how to build the UI with Dash to support using Beam YAML to build Beam pipelines. Contributions are welcome, and the use of GenAI to enhance the project is encouraged.

## File Structure

```
├── beamforge/        # Main application code
│   ├── assets/       # Static assets (CSS, images)
│   ├── callbacks/    # Dash app callback functions
│   ├── layouts/      # Dash app layout definitions
│   └── utils/        # Utility modules
└── catalog/          # Example Beam YAML pipeline definitions
    └── examples/     # Specific example YAML files
```

## Quick Start

```bash
make help        # Print this help
make init        # Init virtual environment
make format      # Run formatter on source code
make lint        # Run linter on source code
make clean-lite  # Remove pycache files, pytest files, etc
make clean       # Remove virtual environment, downloaded models, etc
make run         # Run the application
```
