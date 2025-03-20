# Analog Devices Companion Chip Parser

A Python script to extract companion parts, alternative parts, and catalog hierarchy from Analog Devices product pages.

## Features

- Extracts companion parts and alternative parts from Analog Devices product pages
- Extracts catalog hierarchy (breadcrumb navigation) from product pages
- Handles dynamic tab-based content
- Provides debug output for HTML inspection
- Robust error handling and logging

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd chip_relationship_parser
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install requests beautifulsoup4
```

## Usage

Run the script directly:
```bash
python companion_chip_parser.py
```

Or import the function in your code:
```python
from companion_chip_parser import get_parts

url = "https://www.analog.com/en/products/ad5314.html"
companion_parts, alternative_parts, catalog_hierarchy = get_parts(url)
```

## Output

The script returns a tuple containing three lists:
1. `companion_parts`: List of companion part numbers (e.g., ['ad820', 'ad8638', ...])
2. `alternative_parts`: List of alternative part numbers (e.g., ['ad5317r'])
3. `catalog_hierarchy`: List of catalog hierarchy levels (e.g., ['Home', 'Products', 'D/A Converters (DAC)', ...])

Example output:
```
Catalog Hierarchy:
Home > Products > D/A Converters (DAC) > Precision D/A Converters > Voltage Output D/A Converters > Multichannel Voltage Output D/A Converters > AD5314

Total hierarchy levels: 7

Companion Parts:
- ad820
- ad8638
- ad8639
- op295
- ref195
- adr4550
- adr435
- ref192
- adr3425
- adr4525
- adum1300
- adum1310

Total companion parts found: 12

Alternative Parts:
- ad5317r

Total alternative parts found: 1
```

## Debug Output

The script saves the HTML response to `debug_output/ad5314.html` for inspection purposes. This can be helpful for:
- Debugging parsing issues
- Understanding the page structure
- Verifying the content being processed

## Error Handling

The script includes comprehensive error handling for:
- Network request failures
- HTML parsing errors
- Missing or malformed content

## Dependencies

- Python 3.6+
- requests
- beautifulsoup4

## License

[Your chosen license]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 