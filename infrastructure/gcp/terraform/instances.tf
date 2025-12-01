# Control Node (Attacker Machine)
resource "google_compute_instance" "control_node" {
  name         = "metalllm-control"
  machine_type = "n1-standard-2"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 50
      type  = "pd-standard"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.attacker.id
  }

  metadata = {
    enable-oslogin = "TRUE"
  }

  metadata_startup_script = file("${path.module}/../scripts/setup_control_node.sh")

  scheduling {
    preemptible                 = var.use_spot_instances
    automatic_restart           = !var.use_spot_instances
    on_host_maintenance         = var.use_spot_instances ? "TERMINATE" : "MIGRATE"
    provisioning_model          = var.use_spot_instances ? "SPOT" : "STANDARD"
    instance_termination_action = var.use_spot_instances ? "STOP" : null
  }

  service_account {
    scopes = ["cloud-platform"]
  }

  tags = ["metalllm-lab", "control-node"]

  labels = {
    environment = "test-lab"
    role        = "control"
  }
}

# LLM Target 1: Ollama with GPU
resource "google_compute_instance" "ollama_target" {
  count        = var.enable_gpu ? 1 : 0
  name         = "metalllm-ollama-target"
  machine_type = "n1-standard-4"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 100
      type  = "pd-standard"
    }
  }

  guest_accelerator {
    type  = "nvidia-tesla-t4"
    count = 1
  }

  network_interface {
    subnetwork = google_compute_subnetwork.llm_targets.id
  }

  metadata = {
    enable-oslogin        = "TRUE"
    install-nvidia-driver = "True"
  }

  metadata_startup_script = file("${path.module}/../scripts/setup_ollama.sh")

  scheduling {
    preemptible                 = var.use_spot_instances
    automatic_restart           = !var.use_spot_instances
    on_host_maintenance         = "TERMINATE"  # Required for GPU
    provisioning_model          = var.use_spot_instances ? "SPOT" : "STANDARD"
    instance_termination_action = var.use_spot_instances ? "STOP" : null
  }

  service_account {
    scopes = ["cloud-platform"]
  }

  tags = ["metalllm-lab", "llm-target"]

  labels = {
    environment = "test-lab"
    role        = "llm-target"
    model       = "ollama"
  }
}

# LLM Target 2: vLLM Server with GPU
resource "google_compute_instance" "vllm_target" {
  count        = var.enable_gpu ? 1 : 0
  name         = "metalllm-vllm-target"
  machine_type = "n1-standard-4"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 100
      type  = "pd-standard"
    }
  }

  guest_accelerator {
    type  = "nvidia-tesla-t4"
    count = 1
  }

  network_interface {
    subnetwork = google_compute_subnetwork.llm_targets.id
  }

  metadata = {
    enable-oslogin        = "TRUE"
    install-nvidia-driver = "True"
  }

  metadata_startup_script = file("${path.module}/../scripts/setup_vllm.sh")

  scheduling {
    preemptible                 = var.use_spot_instances
    automatic_restart           = !var.use_spot_instances
    on_host_maintenance         = "TERMINATE"
    provisioning_model          = var.use_spot_instances ? "SPOT" : "STANDARD"
    instance_termination_action = var.use_spot_instances ? "STOP" : null
  }

  service_account {
    scopes = ["cloud-platform"]
  }

  tags = ["metalllm-lab", "llm-target"]

  labels = {
    environment = "test-lab"
    role        = "llm-target"
    model       = "vllm"
  }
}

# RAG Target: Qdrant Vector DB
resource "google_compute_instance" "qdrant_target" {
  name         = "metalllm-qdrant-target"
  machine_type = "n1-standard-2"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 50
      type  = "pd-standard"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.rag_targets.id
  }

  metadata = {
    enable-oslogin = "TRUE"
  }

  metadata_startup_script = file("${path.module}/../scripts/setup_qdrant.sh")

  scheduling {
    preemptible                 = var.use_spot_instances
    automatic_restart           = !var.use_spot_instances
    on_host_maintenance         = var.use_spot_instances ? "TERMINATE" : "MIGRATE"
    provisioning_model          = var.use_spot_instances ? "SPOT" : "STANDARD"
    instance_termination_action = var.use_spot_instances ? "STOP" : null
  }

  service_account {
    scopes = ["cloud-platform"]
  }

  tags = ["metalllm-lab", "rag-target"]

  labels = {
    environment = "test-lab"
    role        = "rag-target"
    service     = "qdrant"
  }
}

# Agent Target: LangChain Server
resource "google_compute_instance" "langchain_target" {
  name         = "metalllm-langchain-target"
  machine_type = "n1-standard-2"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 50
      type  = "pd-standard"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.agent_targets.id
  }

  metadata = {
    enable-oslogin = "TRUE"
  }

  metadata_startup_script = file("${path.module}/../scripts/setup_langchain.sh")

  scheduling {
    preemptible                 = var.use_spot_instances
    automatic_restart           = !var.use_spot_instances
    on_host_maintenance         = var.use_spot_instances ? "TERMINATE" : "MIGRATE"
    provisioning_model          = var.use_spot_instances ? "SPOT" : "STANDARD"
    instance_termination_action = var.use_spot_instances ? "STOP" : null
  }

  service_account {
    scopes = ["cloud-platform"]
  }

  tags = ["metalllm-lab", "agent-target"]

  labels = {
    environment = "test-lab"
    role        = "agent-target"
    framework   = "langchain"
  }
}

# MLOps Target: MLflow Server
resource "google_compute_instance" "mlflow_target" {
  name         = "metalllm-mlflow-target"
  machine_type = "n1-standard-2"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 50
      type  = "pd-standard"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.mlops_targets.id
  }

  metadata = {
    enable-oslogin = "TRUE"
  }

  metadata_startup_script = file("${path.module}/../scripts/setup_mlflow.sh")

  scheduling {
    preemptible                 = var.use_spot_instances
    automatic_restart           = !var.use_spot_instances
    on_host_maintenance         = var.use_spot_instances ? "TERMINATE" : "MIGRATE"
    provisioning_model          = var.use_spot_instances ? "SPOT" : "STANDARD"
    instance_termination_action = var.use_spot_instances ? "STOP" : null
  }

  service_account {
    scopes = ["cloud-platform"]
  }

  tags = ["metalllm-lab", "mlops-target"]

  labels = {
    environment = "test-lab"
    role        = "mlops-target"
    service     = "mlflow"
  }
}
