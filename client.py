"""
checkout-ab-test-skill: Client SDK
Design, simulate, and analyze A/B tests for e-commerce checkout flows.
"""

from __future__ import annotations
import math
from typing import Literal, Optional

ConfidenceLevel = Literal[0.90, 0.95, 0.99]

# Z-scores for one-tailed test
Z_SCORES = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326}
# Two-tailed critical z-scores
Z_TWO_TAILED = {0.90: 1.645, 0.95: 1.960, 0.99: 2.576}


class ABTestClient:
    """
    SDK for analyzing A/B test results in e-commerce checkout flows.

    Implements two-proportion z-test for statistical significance.
    Calculates conversion lift, revenue impact, and provides recommendations.
    """

    def analyze(
        self,
        control: dict,
        variant: dict,
        confidence_level: float = 0.95,
        test_name: str = "Checkout A/B Test",
        monthly_traffic: Optional[int] = None,
    ) -> dict:
        """
        Analyze A/B test results.

        Args:
            control: Dict with keys:
                     - visitors (int): Traffic to control.
                     - conversions (int): Conversions in control.
                     - avg_order_value (float): Average order value in control.
            variant: Same structure as control.
            confidence_level: 0.90, 0.95, or 0.99.
            test_name: Human-readable test name.
            monthly_traffic: Optional total monthly traffic for revenue projection.

        Returns:
            dict with analysis results and recommendation.
        """
        ctrl_v = int(control["visitors"])
        ctrl_c = int(control["conversions"])
        var_v = int(variant["visitors"])
        var_c = int(variant["conversions"])
        ctrl_aov = float(control.get("avg_order_value", 0))
        var_aov = float(variant.get("avg_order_value", ctrl_aov))

        if ctrl_v == 0 or var_v == 0:
            raise ValueError("Visitors count must be greater than 0.")

        ctrl_cr = ctrl_c / ctrl_v
        var_cr = var_c / var_v

        # Two-proportion z-test
        p_pool = (ctrl_c + var_c) / (ctrl_v + var_v)
        se = math.sqrt(p_pool * (1 - p_pool) * (1 / ctrl_v + 1 / var_v))
        z_stat = (var_cr - ctrl_cr) / se if se > 0 else 0
        p_value = self._z_to_p(z_stat)

        z_critical = Z_TWO_TAILED.get(confidence_level, 1.96)
        is_significant = abs(z_stat) >= z_critical

        # Lift
        lift = ((var_cr - ctrl_cr) / ctrl_cr * 100) if ctrl_cr > 0 else 0

        # Revenue impact
        base_traffic = monthly_traffic or max(ctrl_v, var_v) * 2
        extra_conversions_per_month = (var_cr - ctrl_cr) * base_traffic
        revenue_impact = extra_conversions_per_month * var_aov

        # Sample size check
        min_sample = self._min_sample_size(ctrl_cr, confidence_level)
        sufficient_sample = ctrl_v >= min_sample and var_v >= min_sample

        # Recommendation
        recommendation = self._recommend(is_significant, lift, sufficient_sample)

        # Power calculation
        power = self._statistical_power(ctrl_cr, var_cr, ctrl_v, var_v, confidence_level)

        summary = self._build_summary(
            test_name, ctrl_cr, var_cr, lift, p_value,
            confidence_level, is_significant, revenue_impact, recommendation
        )

        return {
            "test_name": test_name,
            "control": {
                "visitors": ctrl_v, "conversions": ctrl_c,
                "conversion_rate": round(ctrl_cr * 100, 3),
                "avg_order_value": ctrl_aov,
            },
            "variant": {
                "visitors": var_v, "conversions": var_c,
                "conversion_rate": round(var_cr * 100, 3),
                "avg_order_value": var_aov,
            },
            "is_significant": is_significant,
            "confidence_level": confidence_level,
            "z_statistic": round(z_stat, 4),
            "p_value": round(p_value, 4),
            "conversion_lift_pct": round(lift, 2),
            "revenue_impact_usd": round(revenue_impact, 2),
            "statistical_power": round(power * 100, 1),
            "sufficient_sample": sufficient_sample,
            "min_sample_per_group": min_sample,
            "recommendation": recommendation,
            "summary": summary,
        }

    def design_test(
        self,
        baseline_cr: float,
        min_detectable_effect: float = 0.05,
        confidence_level: float = 0.95,
        power: float = 0.80,
    ) -> dict:
        """
        Calculate required sample size to detect a minimum effect.

        Args:
            baseline_cr: Current conversion rate (e.g., 0.03 for 3%).
            min_detectable_effect: Minimum relative lift to detect (e.g., 0.05 for 5%).
            confidence_level: Statistical confidence level.
            power: Desired statistical power (default 0.80).

        Returns:
            dict with required sample size per group and estimated test duration.
        """
        target_cr = baseline_cr * (1 + min_detectable_effect)
        z_alpha = Z_TWO_TAILED.get(confidence_level, 1.96)
        z_beta = {0.80: 0.842, 0.90: 1.282, 0.95: 1.645}.get(power, 0.842)

        p_avg = (baseline_cr + target_cr) / 2
        n = (z_alpha + z_beta) ** 2 * p_avg * (1 - p_avg) / (target_cr - baseline_cr) ** 2
        n = math.ceil(n)

        return {
            "baseline_conversion_rate": round(baseline_cr * 100, 2),
            "target_conversion_rate": round(target_cr * 100, 2),
            "min_detectable_effect_pct": round(min_detectable_effect * 100, 1),
            "required_sample_per_group": n,
            "total_required_sample": n * 2,
            "confidence_level": confidence_level,
            "statistical_power": power,
        }

    def simulate(self, n_tests: int = 100, true_lift: float = 0.0, traffic_per_group: int = 5000) -> dict:
        """
        Run Monte Carlo simulation to estimate false positive/negative rates.
        """
        import random
        baseline_cr = 0.03
        variant_cr = baseline_cr * (1 + true_lift)
        significant_count = 0
        for _ in range(n_tests):
            ctrl_c = sum(1 for _ in range(traffic_per_group) if random.random() < baseline_cr)
            var_c = sum(1 for _ in range(traffic_per_group) if random.random() < variant_cr)
            result = self.analyze(
                control={"visitors": traffic_per_group, "conversions": ctrl_c, "avg_order_value": 50},
                variant={"visitors": traffic_per_group, "conversions": var_c, "avg_order_value": 50},
            )
            if result["is_significant"]:
                significant_count += 1
        rate = significant_count / n_tests
        return {
            "n_simulations": n_tests,
            "true_lift": true_lift,
            "detection_rate": round(rate, 3),
            "type_1_error_rate" if true_lift == 0 else "power_estimate": round(rate, 3),
        }

    @staticmethod
    def _z_to_p(z: float) -> float:
        """Approximate p-value from z-statistic (two-tailed)."""
        z = abs(z)
        t = 1 / (1 + 0.2316419 * z)
        poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
        phi = 1 - (1 / math.sqrt(2 * math.pi)) * math.exp(-z * z / 2) * poly
        return round(2 * (1 - phi), 6)

    @staticmethod
    def _min_sample_size(baseline_cr: float, confidence_level: float) -> int:
        z = Z_TWO_TAILED.get(confidence_level, 1.96)
        if baseline_cr <= 0 or baseline_cr >= 1:
            return 1000
        n = (z ** 2 * baseline_cr * (1 - baseline_cr)) / (0.1 * baseline_cr) ** 2
        return max(int(n), 100)

    @staticmethod
    def _statistical_power(p1: float, p2: float, n1: int, n2: int, conf: float) -> float:
        if p1 == p2 or n1 == 0 or n2 == 0:
            return 0.5
        z_alpha = Z_TWO_TAILED.get(conf, 1.96)
        p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
        se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
        se2 = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
        if se2 == 0:
            return 0.5
        z_beta = (abs(p2 - p1) - z_alpha * se) / se2
        # Approximate CDF
        return max(0.0, min(1.0, 0.5 * (1 + math.erf(z_beta / math.sqrt(2)))))

    @staticmethod
    def _recommend(is_significant: bool, lift: float, sufficient_sample: bool) -> str:
        if not sufficient_sample:
            return "Continue testing — insufficient sample size for reliable results."
        if is_significant and lift > 0:
            return "Ship variant — statistically significant positive lift detected."
        if is_significant and lift < 0:
            return "Revert to control — variant shows significant negative impact."
        return "Continue testing — results not yet statistically significant."

    @staticmethod
    def _build_summary(name, ctrl_cr, var_cr, lift, p_value, conf, significant, revenue_impact, recommendation) -> str:
        direction = "increase" if lift > 0 else "decrease"
        sig_str = "statistically significant" if significant else "NOT statistically significant"
        return (
            f"Test: {name} | "
            f"Control CR: {ctrl_cr*100:.2f}% vs Variant CR: {var_cr*100:.2f}% | "
            f"Lift: {lift:+.2f}% ({direction}) | "
            f"p-value: {p_value:.4f} (confidence: {conf*100:.0f}%) | "
            f"Result: {sig_str} | "
            f"Est. Monthly Revenue Impact: ${revenue_impact:+,.2f} | "
            f"Recommendation: {recommendation}"
        )
