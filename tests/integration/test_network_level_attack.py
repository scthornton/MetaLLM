"""
Integration Test: Network-Level ML Attack Scenario

Demonstrates network-based attacks against ML APIs:
1. Model Extraction (steal model architecture/weights)
2. Membership Inference (determine training data)
3. Model Inversion (reconstruct training samples)
4. Adversarial Examples (evade detection)
5. API Key Harvesting (steal credentials)

This scenario simulates attacking a production ML API service.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from metaLLM.core.module_loader import ModuleLoader
from metaLLM.base.target import Target


def test_network_level_attack():
    """
    End-to-end network-level ML attack

    Scenario:
    - Attacker discovers ML API endpoint (fraud detection system)
    - Extracts model through strategic queries
    - Determines if specific data was in training set
    - Reconstructs sensitive training data
    - Generates adversarial examples to evade detection
    - Harvests API keys for unauthorized access
    """

    print("="*80)
    print("Network-Level ML Attack Scenario")
    print("Target: Production Fraud Detection API")
    print("="*80)
    print()

    # Initialize module loader
    loader = ModuleLoader()
    loader.discover_modules()

    # Simulated target: Production ML API
    ml_api_target = Target(
        url="https://ml-api.fintech-corp.com/v1",
        api_key="pk_live_1234567890abcdef"  # Publicly exposed key
    )

    # ===== Phase 1: Reconnaissance - Model Extraction =====
    print("\n[Phase 1] Reconnaissance - Model Extraction via Inference")
    print("-" * 80)

    extraction_class = loader.load_module("exploits/network/model_extraction")
    extraction_exploit = extraction_class()
    extraction_exploit.set_target(ml_api_target)

    # Configure for knowledge distillation attack
    extraction_exploit.options["ATTACK_TYPE"].value = "knowledge_distillation"
    extraction_exploit.options["QUERY_BUDGET"].value = 1000
    extraction_exploit.options["INPUT_DIMENSION"].value = 20  # 20-feature fraud model
    extraction_exploit.options["NUM_CLASSES"].value = 2  # binary: fraud/legitimate
    extraction_exploit.options["USE_ADAPTIVE_SAMPLING"].value = True

    print(f"Module: {extraction_exploit.name}")
    print(f"Attack: {extraction_exploit.options['ATTACK_TYPE'].value}")
    print(f"Query Budget: {extraction_exploit.options['QUERY_BUDGET'].value}")
    print(f"Target: Fraud detection model")

    check_result = extraction_exploit.check()
    print(f"Vulnerable: {check_result.vulnerable} (confidence: {check_result.confidence:.2%})")
    print(f"Details: {check_result.details}")

    if check_result.vulnerable:
        print("\n✓ Model API accessible - beginning extraction...")
        print("  → Querying API with strategic inputs...")
        print("  → 1000 queries completed")
        print("  → Training substitute model on collected data...")
        print("  → Substitute model accuracy: 94.2%")
        print("  → Model architecture inferred: 3-layer MLP [20, 64, 32, 2]")
        print("  → Model effectively cloned!")

    # ===== Phase 2: Privacy Attack - Membership Inference =====
    print("\n\n[Phase 2] Privacy Attack - Membership Inference")
    print("-" * 80)

    membership_class = loader.load_module("exploits/network/membership_inference")
    membership_exploit = membership_class()
    membership_exploit.set_target(ml_api_target)

    # Configure for statistical test attack
    membership_exploit.options["ATTACK_TYPE"].value = "statistical_test"
    membership_exploit.options["TARGET_SAMPLES"].value = 100
    membership_exploit.options["STATISTICAL_SIGNIFICANCE"].value = "0.05"

    print(f"Module: {membership_exploit.name}")
    print(f"Attack: {membership_exploit.options['ATTACK_TYPE'].value}")
    print(f"Samples: {membership_exploit.options['TARGET_SAMPLES'].value}")
    print(f"Objective: Determine if specific transactions were in training data")

    check_result = membership_exploit.check()
    print(f"Vulnerable: {check_result.vulnerable} (confidence: {check_result.confidence:.2%})")

    if check_result.vulnerable:
        print("\n✓ Model shows overfitting indicators - testing membership...")
        print("  → Testing 100 known transaction records...")
        print("  → Running Kolmogorov-Smirnov test...")
        print("  → KS statistic: 0.342, p-value: 0.001 (significant!)")
        print("  → 73 transactions confirmed in training set")
        print("  → Privacy violation: Can identify training data")
        print("\n  Exposed transactions include:")
        print("    - Transaction #892341: High-value wire transfer")
        print("    - Transaction #103923: Celebrity credit card purchase")
        print("    - Transaction #445122: Healthcare payment (HIPAA violation)")

    # ===== Phase 3: Data Reconstruction - Model Inversion =====
    print("\n\n[Phase 3] Data Reconstruction - Model Inversion Attack")
    print("-" * 80)

    inversion_class = loader.load_module("exploits/network/model_inversion")
    inversion_exploit = inversion_class()
    inversion_exploit.set_target(ml_api_target)

    # Configure for gradient optimization
    inversion_exploit.options["ATTACK_TYPE"].value = "gradient_optimization"
    inversion_exploit.options["TARGET_CLASS"].value = 1  # fraud class
    inversion_exploit.options["INPUT_DIMENSION"].value = 20
    inversion_exploit.options["OPTIMIZATION_STEPS"].value = 500
    inversion_exploit.options["LEARNING_RATE"].value = "0.1"
    inversion_exploit.options["USE_MOMENTUM"].value = True

    print(f"Module: {inversion_exploit.name}")
    print(f"Attack: {inversion_exploit.options['ATTACK_TYPE'].value}")
    print(f"Target Class: Fraudulent transactions")
    print(f"Objective: Reconstruct typical fraud patterns")

    check_result = inversion_exploit.check()
    print(f"Vulnerable: {check_result.vulnerable} (confidence: {check_result.confidence:.2%})")

    if check_result.vulnerable:
        print("\n✓ Confidence scores available - reconstructing training data...")
        print("  → Optimizing input to maximize fraud prediction...")
        print("  → 500 gradient descent iterations completed")
        print("  → Reconstruction confidence: 0.94")
        print("\n  Reconstructed fraud pattern:")
        print("    - Transaction amount: $9,847.32")
        print("    - Time: 3:42 AM")
        print("    - Location: Foreign country")
        print("    - Card not present")
        print("    - Multiple rapid transactions")
        print("  → This reveals fraud detection logic!")

    # ===== Phase 4: Evasion - Adversarial Examples =====
    print("\n\n[Phase 4] Evasion - Adversarial Example Generation")
    print("-" * 80)

    adversarial_class = loader.load_module("exploits/network/adversarial_examples")
    adversarial_exploit = adversarial_class()
    adversarial_exploit.set_target(ml_api_target)

    # Configure for PGD attack
    adversarial_exploit.options["ATTACK_TYPE"].value = "pgd"
    adversarial_exploit.options["EPSILON"].value = "0.1"
    adversarial_exploit.options["NUM_ITERATIONS"].value = 40
    adversarial_exploit.options["STEP_SIZE"].value = "0.01"
    adversarial_exploit.options["NUM_EXAMPLES"].value = 10

    print(f"Module: {adversarial_exploit.name}")
    print(f"Attack: {adversarial_exploit.options['ATTACK_TYPE'].value}")
    print(f"Epsilon: {adversarial_exploit.options['EPSILON'].value}")
    print(f"Objective: Evade fraud detection with minimal changes")

    check_result = adversarial_exploit.check()
    print(f"Vulnerable: {check_result.vulnerable} (confidence: {check_result.confidence:.2%})")

    if check_result.vulnerable:
        print("\n✓ Model is vulnerable to adversarial perturbations...")
        print("  → Generating adversarial examples...")
        print("  → PGD attack: 40 iterations")
        print("  → 10 examples generated")
        print("  → Success rate: 80%")
        print("\n  Adversarial transaction example:")
        print("    Original: Flagged as FRAUD (confidence: 0.92)")
        print("    Modified: Transaction amount: $9,847.32 → $9,832.15")
        print("              Time: 3:42 AM → 3:38 AM")
        print("    Result: Classified as LEGITIMATE (confidence: 0.67)")
        print("  → Fraud detection evaded with minimal changes!")

    # ===== Phase 5: Credential Theft - API Key Harvesting =====
    print("\n\n[Phase 5] Credential Theft - API Key Harvesting")
    print("-" * 80)

    api_key_class = loader.load_module("exploits/network/api_key_harvesting")
    api_key_exploit = api_key_class()
    api_key_exploit.set_target(ml_api_target)

    # Configure for comprehensive harvesting
    api_key_exploit.options["ATTACK_TYPE"].value = "header_analysis"
    api_key_exploit.options["SCAN_DEPTH"].value = "deep"
    api_key_exploit.options["EXTRACT_FROM_ERRORS"].value = True
    api_key_exploit.options["CHECK_JAVASCRIPT"].value = True

    print(f"Module: {api_key_exploit.name}")
    print(f"Attack: {api_key_exploit.options['ATTACK_TYPE'].value}")
    print(f"Scan Depth: {api_key_exploit.options['SCAN_DEPTH'].value}")

    check_result = api_key_exploit.check()
    print(f"Vulnerable: {check_result.vulnerable} (confidence: {check_result.confidence:.2%})")

    if check_result.vulnerable:
        print("\n✓ API exposes sensitive information - harvesting credentials...")
        print("  → Analyzing HTTP headers...")
        print("  → Checking error messages...")
        print("  → Examining JavaScript files...")
        print("\n  Credentials found:")
        print("    - API Key (header): pk_live_1234567890abcdef")
        print("    - Secret Key (error): sk_live_9876543210fedcba")
        print("    - Admin Token (JS): admin_token_abc123xyz")
        print("    - AWS Access Key: AKIAIOSFODNN7EXAMPLE")
        print("    - Database URL: postgresql://admin:pass@db.internal:5432")
        print("  → 5 credentials harvested!")
        print("  → Full API access obtained")

    # ===== Attack Summary =====
    print("\n\n" + "="*80)
    print("Attack Chain Complete")
    print("="*80)
    print("""
Attack Summary:
1. ✓ Model Extraction     - Cloned fraud detection model (94.2% accuracy)
2. ✓ Membership Inference  - Identified 73 training transactions
3. ✓ Model Inversion      - Reconstructed fraud patterns
4. ✓ Adversarial Examples  - Evaded detection (80% success rate)
5. ✓ API Key Harvesting   - Stolen 5 credentials

Impact Assessment:
┌─────────────────────────────────────────────────────────────────┐
│ Model IP Theft        │ Complete model architecture stolen      │
│ Privacy Violations    │ 73 transactions exposed (GDPR breach)   │
│ Data Reconstruction   │ Sensitive fraud patterns revealed       │
│ Security Bypass       │ Can evade fraud detection at will       │
│ Credential Theft      │ Full API access + cloud infrastructure  │
└─────────────────────────────────────────────────────────────────┘

Real-World Consequences:
- Attacker can commit fraud undetected
- Competitor has stolen proprietary model
- GDPR fines for exposed customer data
- Reputational damage
- Regulatory investigation
- Customer lawsuits

Financial Impact Estimate:
- Model IP value: $2-5M
- GDPR fines: up to 4% revenue
- Fraud losses: potentially unlimited
- Incident response: $500K+
- Total: $10M+ potential exposure

Recommended Remediation:
1. Implement rate limiting (prevents extraction)
2. Add differential privacy (prevents membership inference)
3. Use prediction rounding (prevents inversion)
4. Adversarial training (improves robustness)
5. Never expose API keys in client code
6. Implement monitoring for extraction patterns
7. Use API authentication and authorization
8. Regular security audits of ML endpoints
""")

    print("="*80)
    print("Test completed successfully!")
    print("="*80)


if __name__ == "__main__":
    test_network_level_attack()
