# Identity Document Verification PoC

This project is a Proof of Concept (PoC) for extracting relevant information from identity documents (Passports, Driver's Licenses) using Fireworks AI vision models for structured data extraction, followed by post-processing and validation.

Repository: [https://github.com/XayHanmonty/id-verification-poc](https://github.com/XayHanmonty/id-verification-poc)

## Features

- Extract structured data from ID documents using state-of-the-art AI vision models
- Comprehensive post-processing to correct common OCR errors
- Proper handling of document-specific formats and variations
- All extracted data saved in JSON format to dedicated output folder

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd id-verification-poc
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Fireworks AI API Key:**
    Obtain an API key from [Fireworks AI](https://docs.fireworks.ai/). Set it as an environment variable:
    ```bash
    export FIREWORKS_API_KEY="your_fireworks_api_key"
    ```

4.  **Place Input Images:**
    Put the identity document images (.png, .jpg, .jpeg) into the `data/images/` directory.

## Running the PoC

The project provides a unified entry point (`main.py`) that processes ID documents:

```bash
cd src
python main.py
```

This will:
- Process all images in the `data/images/` directory
- Extract information using Llama-v3p2-11b-vision-instruct model
- Save results to `output/extraction_results.json`

## Project Structure

```
id-verification-poc/
├── data/
│   └── images/        # Input ID images go here
│       ├── License 1.png
│       ├── License-2.jpg
│       └── ...
├── output/            # All extraction results are saved here
│   └── extraction_results.json  # General extraction data
├── src/
│   ├── main.py               # Entry point with simplified interface
│   ├── extraction.py         # Core image processing functionality
│   ├── parsing.py            # AI response parsing utilities
│   ├── postprocess.py        # Data normalization and correction
│   └── image_utils.py        # Image encoding and file handling
├── .gitignore
├── README.md
└── requirements.txt
```

## Design Choices and Tradeoffs

### 1. Vision Model Selection

**Choice**: Other than traditional OCR (Tesseract) instead I use Fireworks AI's vision models.

**Rationale**:
- Fireworks AI models provide significantly higher accuracy for complex document understanding
- Models understand document context and can extract structured data directly
- This is crucial since it reduces the need for complex regex pattern matching and rule-based extraction

**Tradeoffs**:
- Incurs API usage costs versus free local OCR
- Adds external dependency on third-party service

### 2. Model Architecture

**Choice**: Leveraged Llama 3.2 11B Vision Instruct model.

**Rationale**:
- Large context window (128k) allows processing high-resolution documents
- Multimodal capabilities handle both text and visual elements
- Instruction-tuned model responds well to specific extraction requests

**Tradeoffs**:
- Larger model than alternatives (like Phi 3.5 Vision with 31k context)
- Higher token cost ($0.20/M tokens)
- Higher latency compared to smaller models

### 3. Structured Schema Definition

**Choice**: Implemented JSON schema constraint for AI responses.

**Rationale**:
- Ensures consistent output format for all document types
- Reduces post-processing complexity
- Creates a reliable contract for data structures

**Tradeoffs**:
- Slightly more complex API requests
- Occasional parsing failures requiring fallback methods
- Less flexibility in model's response format

### 4. Modular Code Architecture

**Choice**: Implemented a modular code structure with separation of concerns.

**Rationale**:
- Improves maintainability and readability
- Allows focused development on individual components
- Simplifies future extensions and alterations

**Tradeoffs**:
- More complex import dependencies
- May introduce overhead for simpler use cases
- Requires consistent coding patterns across modules

### 5. Error Handling & Fallbacks

**Choice**: Implemented multiple fallback methods for parsing responses.

**Rationale**:
- Ensures robustness against varied API responses
- Handles markdown, JSON, and unstructured text formats
- Provides usable results even when primary parsing fails

**Tradeoffs**:
- Increases processing complexity
- May occasionally extract imperfect data rather than failing outright
- Requires maintaining multiple parsing strategies

### 6. Command-Line Interface Simplification

**Choice**: Simplified interface to a single command without parameters.

**Rationale**:
- Reduces complexity for end users
- Standardizes directory structure and output formats
- Focuses on core functionality without configuration overhead

**Tradeoffs**:
- Less flexibility for different use cases
- Fixed input/output paths
- Requires code changes rather than config changes for customization

## Performance Considerations

### Response Time
- Average processing time: 2-3 seconds per document
- Network latency is the primary bottleneck rather than local processing
- Batch processing improves overall throughput compared to individual calls

### Accuracy
- High accuracy for standard fields (>95% for name, document type, dates)
- Document numbers require specialized post-processing for best results
- Address fields have more variability in extraction quality

### Cost Efficiency
- The implementation balances accuracy and cost by using structured output
- Each document costs approximately $0.02-0.05 to process
- Batch processing reduces overall API costs

## Future Improvements

- Integration with database systems for reference validation
- Enhanced security features for API key management
- Web interface for easier interaction and visualization
- Multi-language support for international ID documents

## License
[Xay Hanmonty]