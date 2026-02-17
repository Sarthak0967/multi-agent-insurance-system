AVAILABLE_POLICIES = [
    "LIC Jeevan Anand",
    "LIC Tech Term",
    "HDFC Life Click 2 Protect",
    "ICICI Pru iProtect Smart",
    "SBI Life eShield"
]


def validate_policy(user_input):
    """
    Validates user input against available insurance policies.
    Returns:
        - Correct formatted policy name (string) if valid
        - None if invalid
    """

    # Normalize input
    normalized_input = user_input.strip().lower()

    # Normalize policy list
    normalized_policies = [policy.lower() for policy in AVAILABLE_POLICIES]

    # Check exact match (case-insensitive)
    if normalized_input in normalized_policies:
        index = normalized_policies.index(normalized_input)
        return AVAILABLE_POLICIES[index]

    return None
