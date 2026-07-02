"""
example_usage.py -- Demonstrates the ABTestClient SDK.
"""
from client import ABTestClient

def main():
    client = ABTestClient()

    # 1. Analyze a completed test
    print("[1] Checkout A/B Test Analysis")
    result = client.analyze(
        control={"visitors": 12500, "conversions": 375, "avg_order_value": 85.50},
        variant={"visitors": 12500, "conversions": 432, "avg_order_value": 88.20},
        confidence_level=0.95,
        test_name="One-Page Checkout vs Multi-Step",
        monthly_traffic=50000,
    )
    print(f"Test: {result['test_name']}")
    print(f"Control CR: {result['control']['conversion_rate']}%")
    print(f"Variant CR: {result['variant']['conversion_rate']}%")
    print(f"Lift: {result['conversion_lift_pct']:+.2f}%")
    print(f"p-value: {result['p_value']} | Significant: {result['is_significant']}")
    print(f"Statistical Power: {result['statistical_power']}%")
    print(f"Revenue Impact: ${result['revenue_impact_usd']:,.2f}/month")
    print(f"Recommendation: {result['recommendation']}")

    # 2. Design a test (sample size planning)
    print("\n[2] Test Design -- Sample Size Calculator")
    design = client.design_test(
        baseline_cr=0.025,
        min_detectable_effect=0.10,
        confidence_level=0.95,
        power=0.80,
    )
    print(f"Baseline CR: {design['baseline_conversion_rate']}%")
    print(f"Target CR: {design['target_conversion_rate']}%")
    print(f"Required sample per group: {design['required_sample_per_group']:,}")
    print(f"Total required: {design['total_required_sample']:,} visitors")

    # 3. Negative result example
    print("\n[3] Non-Significant Test Result")
    result2 = client.analyze(
        control={"visitors": 800, "conversions": 24, "avg_order_value": 60},
        variant={"visitors": 820, "conversions": 26, "avg_order_value": 62},
        confidence_level=0.95,
        test_name="Express Checkout Button Color",
    )
    print(f"Significant: {result2['is_significant']} | Recommendation: {result2['recommendation']}")
    print(f"Sufficient Sample: {result2['sufficient_sample']} (need {result2['min_sample_per_group']:,} per group)")

if __name__ == "__main__":
    main()
