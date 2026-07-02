# checkout-ab-test-skill

> **GenPark AI Agent Skill** — Design, simulate, and analyze A/B tests for e-commerce checkout flows.

## Features

- Two-proportion z-test for statistical significance
- Conversion lift and revenue impact calculation
- Statistical power estimation
- Sample size calculator (test design)
- Monte Carlo simulation for false positive rates
- Clear Ship / Continue / Revert recommendations

## Quick Start

```python
from client import ABTestClient

client = ABTestClient()
result = client.analyze(
    control={"visitors": 10000, "conversions": 300, "avg_order_value": 80},
    variant={"visitors": 10000, "conversions": 340, "avg_order_value": 82},
    confidence_level=0.95,
    monthly_traffic=40000,
)
print(result["recommendation"])
print(f"Revenue impact: ${result['revenue_impact_usd']:,.2f}/month")
```

## Installation

```bash
python example_usage.py  # No external dependencies
```

---
Built by [GenPark](https://genpark.ai) | [alphaparkinc](https://github.com/alphaparkinc)
