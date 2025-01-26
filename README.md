# CRAAPER - CRAAP Test Analysis Tool

CRAAPER is a Python-based tool that automates the [CRAAP test](https://library.csuchico.edu/help/source-or-information-good) analysis for academic sources using AI. It helps researchers and students evaluate the quality and reliability of their sources by analyzing Currency, Relevance, Authority, Accuracy, and Purpose.

## Features

- **Automated CRAAP Analysis**: Uses GPT-4 to analyze academic sources based on the CRAAP criteria
- **BibTeX Integration**: Directly processes BibTeX files for batch analysis
- **Smart Caching**: Caches analysis results to avoid redundant API calls and save costs
- **Detailed Scoring**:
  - Individual scores (0-10) for each CRAAP criterion
  - Total score (0-50) with categorization
  - Confidence levels for each assessment
  - Detailed explanations for each criterion
- **Scoring Categories**:
  - 45-50: Excellent
  - 40-44: Good
  - 35-39: Average
  - 30-34: Borderline
  - <30: Unreliable, not suitable for use
- **Rich Output Format**:
  - Summary table with all scores
  - Detailed explanations for each source
  - Confidence indicators for less certain assessments

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/craaper.git
cd craaper
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:

```bash
touch .env
```

4. Add your OpenAI API key to the `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Prepare your BibTeX file with your sources.

2. Run the analysis:

```bash
python src/main.py path/to/your/references.bib
```

3. Review the output which includes:
   - A summary table with scores for each criterion
   - Total scores and categories
   - Detailed explanations for each assessment
   - Confidence indicators (marked with \*) for less certain evaluations

## Cache Management

The tool automatically caches analysis results in `~/.craaper/cache/analysis_cache.json` to:

- Avoid redundant API calls
- Save costs on repeated analyses
- Speed up subsequent runs

The cache is based on the content hash of each bibliography entry, ensuring that only changed entries trigger new analyses.

## Output Format

The tool provides a comprehensive output including:

- A summary table with all scores and categories
- Scoring category legend
- Detailed explanations for each source
- Confidence indicators for assessments
- Total scores and their corresponding categories

## Requirements

- Python 3.8+
- OpenAI API key
- Required Python packages (see requirements.txt)

## Note on API Usage

This tool uses the OpenAI GPT-4 API, which incurs costs based on token usage. The caching mechanism helps minimize these costs by reusing previous analyses when possible.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
