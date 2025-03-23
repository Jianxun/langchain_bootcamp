# ADI Engineer Agent Test Sessions

## Overview
This document provides example test sessions demonstrating various use cases and scenarios for the ADI Engineer Agent.

## Basic Product Search Session

### Input
```python
query = "I need an instrumentation amplifier for a sensor interface with 3.3V supply"
```

### Expected Flow
1. Requirements Extraction:
```python
{
    "application_area": "sensor interface",
    "requirements": [
        {
            "parameter": "supply_voltage",
            "unit": "V",
            "min": 3.3,
            "max": 3.3
        }
    ],
    "features": ["instrumentation amplifier"]
}
```

2. Product Search Results:
```python
{
    "total": 5,
    "page": 1,
    "page_size": 10,
    "products": [
        {
            "id": "AD8422",
            "name": "Precision Instrumentation Amplifier",
            "description": "Low power, rail-to-rail instrumentation amplifier...",
            "parameters": {
                "supply_voltage": {
                    "min": 2.7,
                    "max": 5.5,
                    "unit": "V"
                },
                "gain": {
                    "min": 1,
                    "max": 1000,
                    "unit": "V/V"
                }
            },
            "features": ["low power", "rail-to-rail", "precision"],
            "applications": ["sensor interface", "medical instrumentation"],
            "datasheet_url": "https://www.analog.com/media/en/technical-documentation/data-sheets/AD8422.pdf"
        }
    ]
}
```

3. Solution Search Results:
```python
{
    "total": 2,
    "page": 1,
    "page_size": 10,
    "solutions": [
        {
            "id": "CN0428",
            "name": "Temperature Measurement System",
            "description": "Complete temperature measurement solution...",
            "requirements": {
                "supply_voltage": {
                    "min": 2.7,
                    "max": 5.5,
                    "unit": "V"
                }
            },
            "reference_designs": [
                {
                    "id": "CN0428-SCH",
                    "name": "Schematic",
                    "format": "schematic",
                    "url": "https://www.analog.com/media/en/technical-documentation/reference-designs/CN0428-SCH.pdf"
                }
            ],
            "products": [
                {
                    "id": "AD8422",
                    "name": "Precision Instrumentation Amplifier",
                    "role": "signal conditioning"
                }
            ]
        }
    ]
}
```

4. Parameter Analysis:
```python
{
    "comparison": {
        "supply_voltage": {
            "unit": "V",
            "values": {
                "AD8422": {
                    "min": 2.7,
                    "max": 5.5,
                    "value": 3.3
                }
            }
        }
    },
    "validation": {
        "AD8422": {
            "supply_voltage": {
                "status": "valid",
                "message": "Supply voltage within acceptable range"
            }
        }
    },
    "compatibility": {
        "AD8422": {
            "status": "compatible",
            "message": "Product meets all requirements"
        }
    }
}
```

## Complex Solution Search Session

### Input
```python
query = """
Looking for a solution for a precision measurement system:
- Supply voltage: 5V
- Temperature range: -40°C to 85°C
- Need reference design with schematic
- Low power consumption
"""
```

### Expected Flow
1. Requirements Extraction:
```python
{
    "application_area": "precision measurement",
    "requirements": [
        {
            "parameter": "supply_voltage",
            "unit": "V",
            "min": 5.0,
            "max": 5.0
        },
        {
            "parameter": "temperature_range",
            "unit": "°C",
            "min": -40,
            "max": 85
        }
    ],
    "features": ["low power", "reference design", "schematic"]
}
```

2. Solution Search Results:
```python
{
    "total": 3,
    "page": 1,
    "page_size": 10,
    "solutions": [
        {
            "id": "CN0428",
            "name": "Temperature Measurement System",
            "description": "Complete temperature measurement solution...",
            "requirements": {
                "supply_voltage": {
                    "min": 2.7,
                    "max": 5.5,
                    "unit": "V"
                },
                "temperature_range": {
                    "min": -40,
                    "max": 85,
                    "unit": "°C"
                },
                "power_consumption": {
                    "max": 1.5,
                    "unit": "mW"
                }
            },
            "reference_designs": [
                {
                    "id": "CN0428-SCH",
                    "name": "Schematic",
                    "format": "schematic",
                    "url": "https://www.analog.com/media/en/technical-documentation/reference-designs/CN0428-SCH.pdf"
                },
                {
                    "id": "CN0428-LAY",
                    "name": "Layout",
                    "format": "layout",
                    "url": "https://www.analog.com/media/en/technical-documentation/reference-designs/CN0428-LAY.pdf"
                }
            ],
            "products": [
                {
                    "id": "AD8422",
                    "name": "Precision Instrumentation Amplifier",
                    "role": "signal conditioning"
                },
                {
                    "id": "AD7124-8",
                    "name": "Low Power, 24-Bit Sigma-Delta ADC",
                    "role": "analog-to-digital conversion"
                }
            ]
        }
    ]
}
```

3. Parameter Analysis:
```python
{
    "comparison": {
        "supply_voltage": {
            "unit": "V",
            "values": {
                "AD8422": {
                    "min": 2.7,
                    "max": 5.5,
                    "value": 5.0
                },
                "AD7124-8": {
                    "min": 2.7,
                    "max": 5.5,
                    "value": 5.0
                }
            }
        },
        "temperature_range": {
            "unit": "°C",
            "values": {
                "AD8422": {
                    "min": -40,
                    "max": 85
                },
                "AD7124-8": {
                    "min": -40,
                    "max": 85
                }
            }
        }
    },
    "validation": {
        "AD8422": {
            "supply_voltage": {
                "status": "valid",
                "message": "Supply voltage within acceptable range"
            },
            "temperature_range": {
                "status": "valid",
                "message": "Temperature range meets requirements"
            }
        },
        "AD7124-8": {
            "supply_voltage": {
                "status": "valid",
                "message": "Supply voltage within acceptable range"
            },
            "temperature_range": {
                "status": "valid",
                "message": "Temperature range meets requirements"
            }
        }
    },
    "compatibility": {
        "AD8422": {
            "status": "compatible",
            "message": "Product meets all requirements"
        },
        "AD7124-8": {
            "status": "compatible",
            "message": "Product meets all requirements"
        }
    }
}
```

## Error Handling Session

### Input
```python
query = "Find an amplifier with invalid supply voltage 10V"
```

### Expected Flow
1. Requirements Extraction:
```python
{
    "application_area": "amplifier",
    "requirements": [
        {
            "parameter": "supply_voltage",
            "unit": "V",
            "min": 10.0,
            "max": 10.0
        }
    ]
}
```

2. Error Response:
```python
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "No products found matching the specified requirements",
        "details": {
            "parameter": "supply_voltage",
            "value": 10.0,
            "unit": "V",
            "reason": "Value exceeds maximum supported voltage"
        }
    }
}
```

## Performance Test Session

### Input
```python
queries = [
    "Find an amplifier for sensor interface",
    "Need a solution for temperature measurement",
    "Looking for a reference design with schematic"
]
```

### Expected Flow
1. Concurrent Processing:
```python
{
    "total_queries": 3,
    "processing_time": 1.5,  # seconds
    "results": [
        {
            "query": "Find an amplifier for sensor interface",
            "status": "success",
            "processing_time": 0.5
        },
        {
            "query": "Need a solution for temperature measurement",
            "status": "success",
            "processing_time": 0.5
        },
        {
            "query": "Looking for a reference design with schematic",
            "status": "success",
            "processing_time": 0.5
        }
    ]
}
```

## Conclusion
These test sessions demonstrate:
- Basic product search functionality
- Complex solution search with multiple requirements
- Error handling for invalid inputs
- Performance under concurrent load

The sessions cover various aspects of the system's functionality and help ensure:
- Accurate requirement extraction
- Proper product and solution matching
- Comprehensive parameter analysis
- Robust error handling
- Efficient concurrent processing 