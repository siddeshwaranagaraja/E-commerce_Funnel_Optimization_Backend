from typing import Dict, List, Optional
from datetime import datetime
from utils.helpers import safe_divide

def build_insight_payload(
    rule_name: str,
    severity: str,
    description: str,
    value: float,
    recommendation: str,
    context: Optional[Dict] = None
) -> Dict:
    """Build a structured insight payload with consistent schema."""
    return {
        "triggered": True,
        "rule_name": rule_name,
        "severity": severity,
        "description": description,
        "value": round(value, 2),
        "recommendation": recommendation,
        "context": context or {},
        "generated_at": datetime.utcnow().isoformat(),
    }

class RulesEngine:
    """Rule-based insight generation engine."""
    
    # Define thresholds for rule triggering
    HIGH_BROWSE_CART_DROPOFF_THRESHOLD = 50  # 50% dropoff
    HIGH_CART_ABANDONMENT_THRESHOLD = 40  # 40% abandonment
    HIGH_CHECKOUT_ABANDONMENT_THRESHOLD = 30  # 30% abandonment
    LOW_RETURNING_USER_CONVERSION_THRESHOLD = 15  # 15% conversion
    
    @staticmethod
    def check_high_browse_to_cart_dropoff(dropoff_data: Dict) -> Dict:
        """Rule: High browse-to-cart dropoff indicates UX friction."""
        # Extract dropoff value from detailed_dropoff list or direct dict
        if isinstance(dropoff_data, list):
            browse_entry = next((d for d in dropoff_data if d.get("from_stage") == "browse"), {})
            browse_to_cart_dropoff = browse_entry.get("dropoff_rate", 0)
            users_lost = browse_entry.get("dropoff_count", 0)
        else:
            browse_to_cart_dropoff = dropoff_data.get("browse_to_cart_dropoff", 0)
            users_lost = dropoff_data.get("dropoff_count", 0)
        
        if browse_to_cart_dropoff >= RulesEngine.HIGH_BROWSE_CART_DROPOFF_THRESHOLD:
            severity = "high" if browse_to_cart_dropoff >= 70 else "medium"
            return build_insight_payload(
                rule_name="high_browse_cart_dropoff",
                severity=severity,
                description=f"High dropoff from browse to cart ({browse_to_cart_dropoff:.1f}%). "
                            f"Users are not adding products to cart. {users_lost} users lost at this stage.",
                value=browse_to_cart_dropoff,
                recommendation="Improve product discovery, simplify add-to-cart flow, or add product recommendations.",
                context={"stage": "browse_to_cart", "users_lost": users_lost, "threshold": RulesEngine.HIGH_BROWSE_CART_DROPOFF_THRESHOLD}
            )
        
        return {"triggered": False, "rule_name": "high_browse_cart_dropoff"}
    
    @staticmethod
    def check_high_cart_abandonment(behavior_data: Dict) -> Dict:
        """Rule: High cart abandonment indicates checkout friction or pricing concerns."""
        cart_abandonment = behavior_data.get("cart_abandonment", {})
        abandonment_rate = cart_abandonment.get("abandonment_rate", 0)
        abandoned_users = cart_abandonment.get("abandoned_users", 0)
        cart_users = cart_abandonment.get("cart_users", 0)
        avg_sessions = cart_abandonment.get("avg_sessions_before_abandon", 0)
        
        if abandonment_rate >= RulesEngine.HIGH_CART_ABANDONMENT_THRESHOLD:
            severity = "high" if abandonment_rate >= 60 else "medium"
            return build_insight_payload(
                rule_name="high_cart_abandonment",
                severity=severity,
                description=f"High cart abandonment rate ({abandonment_rate:.1f}%). "
                            f"{abandoned_users} of {cart_users} users added items but didn't proceed to checkout. "
                            f"Average {avg_sessions:.1f} sessions before abandonment.",
                value=abandonment_rate,
                recommendation="Implement cart recovery emails, reduce checkout steps, apply discounts, or improve payment options.",
                context={
                    "cart_users": cart_users,
                    "abandoned_users": abandoned_users,
                    "avg_sessions_before_abandon": avg_sessions,
                    "threshold": RulesEngine.HIGH_CART_ABANDONMENT_THRESHOLD
                }
            )
        
        return {"triggered": False, "rule_name": "high_cart_abandonment"}
    
    @staticmethod
    def check_high_checkout_abandonment(behavior_data: Dict) -> Dict:
        """Rule: High checkout abandonment indicates payment or trust issues."""
        checkout_abandonment = behavior_data.get("checkout_abandonment", {})
        abandonment_rate = checkout_abandonment.get("abandonment_rate", 0)
        abandoned_users = checkout_abandonment.get("abandoned_users", 0)
        checkout_users = checkout_abandonment.get("checkout_users", 0)
        device_breakdown = checkout_abandonment.get("device_breakdown", {})
        
        if abandonment_rate >= RulesEngine.HIGH_CHECKOUT_ABANDONMENT_THRESHOLD:
            severity = "critical" if abandonment_rate >= 50 else "high"
            return build_insight_payload(
                rule_name="high_checkout_abandonment",
                severity=severity,
                description=f"High checkout abandonment ({abandonment_rate:.1f}%). "
                            f"{abandoned_users} of {checkout_users} users initiated checkout but didn't complete purchase.",
                value=abandonment_rate,
                recommendation="Add trust badges, simplify payment form, offer guest checkout, provide payment plan options.",
                context={
                    "checkout_users": checkout_users,
                    "abandoned_users": abandoned_users,
                    "device_breakdown": device_breakdown,
                    "threshold": RulesEngine.HIGH_CHECKOUT_ABANDONMENT_THRESHOLD
                }
            )
        
        return {"triggered": False, "rule_name": "high_checkout_abandonment"}
    
    @staticmethod
    def check_weak_returning_user_conversion(behavior_data: Dict, segment_patterns: Dict) -> Dict:
        """Rule: Weak conversion for returning/repeat users."""
        repeated_browse = behavior_data.get("repeated_browse", [])
        returning_user_count = len(repeated_browse)
        
        if returning_user_count > 0:
            # All repeated browse users are stuck — they haven't converted to cart
            purchase_rate = 0.0  # By definition, repeated_browse users are stuck at browse
            
            if purchase_rate < RulesEngine.LOW_RETURNING_USER_CONVERSION_THRESHOLD:
                return build_insight_payload(
                    rule_name="weak_returning_user_conversion",
                    severity="medium",
                    description=f"{returning_user_count} users are repeatedly browsing without converting. "
                                f"These high-intent users are failing to move to the cart stage.",
                    value=purchase_rate,
                    recommendation="Implement personalization, send targeted recommendations, offer incentives for repeat visitors.",
                    context={
                        "returning_user_count": returning_user_count,
                        "threshold": RulesEngine.LOW_RETURNING_USER_CONVERSION_THRESHOLD,
                        "top_users": [u.get("user_id") for u in repeated_browse[:5]]
                    }
                )
        
        return {"triggered": False, "rule_name": "weak_returning_user_conversion"}
    
    @classmethod
    def run_all_rules(cls, funnel_data: Dict, dropoff_data: Dict, behavior_data: Dict, trends_data: Dict = None) -> List[Dict]:
        """Execute all rules and return triggered insights."""
        insights = []
        
        # Check browse-to-cart dropoff (pass full detailed_dropoff list)
        detailed_dropoff = dropoff_data.get("detailed_dropoff", [])
        dropoff_insight = cls.check_high_browse_to_cart_dropoff(detailed_dropoff)
        if dropoff_insight.get("triggered"):
            insights.append(dropoff_insight)
        
        # Check cart abandonment
        cart_insight = cls.check_high_cart_abandonment(behavior_data)
        if cart_insight.get("triggered"):
            insights.append(cart_insight)
        
        # Check checkout abandonment
        checkout_insight = cls.check_high_checkout_abandonment(behavior_data)
        if checkout_insight.get("triggered"):
            insights.append(checkout_insight)
        
        # Check returning user conversion
        returning_insight = cls.check_weak_returning_user_conversion(behavior_data, behavior_data.get("segment_patterns", {}))
        if returning_insight.get("triggered"):
            insights.append(returning_insight)
        
        # Sort by severity (critical > high > medium)
        severity_order = {"critical": 0, "high": 1, "medium": 2}
        insights.sort(key=lambda x: severity_order.get(x.get("severity"), 3))
        
        return insights
        
        if browse_to_cart_dropoff >= RulesEngine.HIGH_BROWSE_CART_DROPOFF_THRESHOLD:
            return {
                "triggered": True,
                "rule_name": "high_browse_cart_dropoff",
                "severity": "high" if browse_to_cart_dropoff >= 70 else "medium",
                "description": f"High dropoff from browse to cart ({browse_to_cart_dropoff:.1f}%). "
                              f"Users are not adding products to cart.",
                "value": browse_to_cart_dropoff,
                "recommendation": "Improve product discovery, simplify add-to-cart flow, or add product recommendations."
            }
        
        return {"triggered": False}
    
    @staticmethod
    def check_high_cart_abandonment(behavior_data: Dict) -> Dict:
        """Rule: High cart abandonment indicates checkout friction or pricing concerns."""
        cart_abandonment = behavior_data.get("cart_abandonment", {})
        abandonment_rate = cart_abandonment.get("abandonment_rate", 0)
        
        if abandonment_rate >= RulesEngine.HIGH_CART_ABANDONMENT_THRESHOLD:
            return {
                "triggered": True,
                "rule_name": "high_cart_abandonment",
                "severity": "high" if abandonment_rate >= 60 else "medium",
                "description": f"High cart abandonment rate ({abandonment_rate:.1f}%). "
                              f"{cart_abandonment.get('abandoned_users', 0)} users added items but didn't proceed to checkout.",
                "value": abandonment_rate,
                "recommendation": "Implement cart recovery emails, reduce checkout steps, apply discounts, or improve payment options."
            }
        
        return {"triggered": False}
    
    @staticmethod
    def check_high_checkout_abandonment(behavior_data: Dict) -> Dict:
        """Rule: High checkout abandonment indicates payment or trust issues."""
        checkout_abandonment = behavior_data.get("checkout_abandonment", {})
        abandonment_rate = checkout_abandonment.get("abandonment_rate", 0)
        
        if abandonment_rate >= RulesEngine.HIGH_CHECKOUT_ABANDONMENT_THRESHOLD:
            return {
                "triggered": True,
                "rule_name": "high_checkout_abandonment",
                "severity": "critical" if abandonment_rate >= 50 else "high",
                "description": f"High checkout abandonment ({abandonment_rate:.1f}%). "
                              f"{checkout_abandonment.get('abandoned_users', 0)} users initiated checkout but didn't complete purchase.",
                "value": abandonment_rate,
                "recommendation": "Add trust badges, simplify payment form, offer guest checkout, provide payment plan options."
            }
        
        return {"triggered": False}
    
    @staticmethod
    def check_weak_returning_user_conversion(behavior_data: Dict, segment_patterns: Dict) -> Dict:
        """Rule: Weak conversion for returning/repeat users."""
        repeated_browse = behavior_data.get("repeated_browse", [])
        returning_user_count = len(repeated_browse)
        
        if returning_user_count > 0:
            # Calculate conversion for returning users
            purchase_rate = safe_divide(sum(1 for u in repeated_browse if "stuck_at" not in u), returning_user_count) * 100
            
            if purchase_rate < RulesEngine.LOW_RETURNING_USER_CONVERSION_THRESHOLD:
                return {
                    "triggered": True,
                    "rule_name": "weak_returning_user_conversion",
                    "severity": "medium",
                    "description": f"Returning users who repeatedly browse have low conversion ({purchase_rate:.1f}%). "
                                  f"{returning_user_count} users are showing repeat browse behavior without converting.",
                    "value": purchase_rate,
                    "recommendation": "Implement personalization, send targeted recommendations, offer incentives for repeat visitors."
                }
        
        return {"triggered": False}
    
    @classmethod
    def run_all_rules(cls, funnel_data: Dict, dropoff_data: Dict, behavior_data: Dict, trends_data: Dict = None) -> List[Dict]:
        """Execute all rules and return triggered insights."""
        insights = []
        
        # Check browse-to-cart dropoff
        dropoff_insight = cls.check_high_browse_to_cart_dropoff(dropoff_data.get("detailed_dropoff", [{}])[0] if dropoff_data.get("detailed_dropoff") else {})
        if dropoff_insight.get("triggered"):
            insights.append(dropoff_insight)
        
        # Check cart abandonment
        cart_insight = cls.check_high_cart_abandonment(behavior_data)
        if cart_insight.get("triggered"):
            insights.append(cart_insight)
        
        # Check checkout abandonment
        checkout_insight = cls.check_high_checkout_abandonment(behavior_data)
        if checkout_insight.get("triggered"):
            insights.append(checkout_insight)
        
        # Check returning user conversion
        returning_insight = cls.check_weak_returning_user_conversion(behavior_data, behavior_data.get("segment_patterns", {}))
        if returning_insight.get("triggered"):
            insights.append(returning_insight)
        
        # Sort by severity (critical > high > medium)
        severity_order = {"critical": 0, "high": 1, "medium": 2}
        insights.sort(key=lambda x: severity_order.get(x.get("severity"), 3))
        
        return insights