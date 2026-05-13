from typing import Dict, List
from utils.helpers import safe_divide

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
        browse_to_cart_dropoff = dropoff_data.get("browse_to_cart_dropoff", 0)
        
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