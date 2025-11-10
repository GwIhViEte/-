# GEMINI.md

## Project Overview

This project, named "BatchScribe," is a Python-based AI novel generator. It provides a graphical user interface (GUI) built with Tkinter for generating novels of various genres. The application supports multiple AI models, including GPT, Claude, Gemini, and Moonshot, and allows for batch generation, continuation of existing stories, and customization of generation parameters.

The core of the application lies in its asynchronous architecture, utilizing `asyncio` and `aiohttp` to handle concurrent API requests efficiently. This allows for a non-blocking user experience, even when generating multiple novels simultaneously. The application also features a sophisticated prompt engineering system that dynamically constructs prompts based on the selected genre, existing text, and other user-defined parameters.

## Building and Running

### Prerequisites

*   Python 3.7+
*   Dependencies listed in `requirements.txt`

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/147227/BatchScribe.git
    ```
2.  Navigate to the project directory:
    ```bash
    cd BatchScribe
    ```
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To run the application, execute the following command in the project's root directory:

```bash
python main.py
```

This will launch the Tkinter-based GUI.

### Testing

The project uses `pytest` for testing. To run the tests, execute the following command:

```bash
pytest
```

## Development Conventions

*   **Coding Style:** The project follows the PEP 8 style guide for Python code.
*   **Asynchronous Programming:** The project heavily relies on `asyncio` for handling long-running I/O operations, such as API calls, to prevent the GUI from freezing.
*   **Modularity:** The codebase is organized into several modules:
    *   `core`: Contains the core logic for novel generation.
    *   `ui`: Contains the GUI components.
    *   `utils`: Contains utility functions for configuration, file handling, etc.
    *   `templates`: Contains prompt templates for different novel genres.
*   **Configuration:** Application settings are stored in a `novel_generator_config.json` file.
*   **Error Handling:** The application includes error handling and retry mechanisms for API calls to improve robustness.
