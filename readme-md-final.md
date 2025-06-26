# Data Protection Compliance Assessment Tool

A modular, scalable compliance assessment tool for various data protection regulations and industries.

## Features

- Support for multiple data protection regulations (DPDP, GDPR, etc.)
- Industry-specific questionnaires
- Interactive compliance dashboard
- Detailed reports and recommendations
- Export functionality (Excel, CSV)

## Project Structure

- `app.py` - Main entry point
- `config.py` - Configuration settings
- `questionnaire_structure.py` - Questionnaire loading logic
- `scoring.py` - Scoring algorithm
- `ui.py` - UI components and rendering
- `utils.py` - Helper functions
- `Questionnaire/` - JSON questionnaire files:
  - `general.json` - General business questionnaire
  - `finance.json` - Finance industry-specific questionnaire

## Getting Started

### Prerequisites

- Python 3.8 or higher

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   streamlit run app.py
   ```

## Adding New Questionnaires

To add new industry-specific questionnaires:

1. Create a new JSON file in the `Questionnaire` directory
2. Follow the structure of existing questionnaires
3. The file will be automatically detected by the application

## License

[MIT License](LICENSE)
