# VPC Network
resource "google_compute_network" "metalllm_vpc" {
  name                    = "metalllm-test-vpc"
  auto_create_subnetworks = false
  description             = "MetaLLM Test Lab VPC"
}

# Subnets
resource "google_compute_subnetwork" "attacker" {
  name          = "attacker-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.metalllm_vpc.id
}

resource "google_compute_subnetwork" "llm_targets" {
  name          = "llm-targets-subnet"
  ip_cidr_range = "10.0.2.0/24"
  region        = var.region
  network       = google_compute_network.metalllm_vpc.id
}

resource "google_compute_subnetwork" "rag_targets" {
  name          = "rag-targets-subnet"
  ip_cidr_range = "10.0.3.0/24"
  region        = var.region
  network       = google_compute_network.metalllm_vpc.id
}

resource "google_compute_subnetwork" "agent_targets" {
  name          = "agent-targets-subnet"
  ip_cidr_range = "10.0.4.0/24"
  region        = var.region
  network       = google_compute_network.metalllm_vpc.id
}

resource "google_compute_subnetwork" "mlops_targets" {
  name          = "mlops-targets-subnet"
  ip_cidr_range = "10.0.5.0/24"
  region        = var.region
  network       = google_compute_network.metalllm_vpc.id
}

# Cloud NAT for outbound internet
resource "google_compute_router" "nat_router" {
  name    = "metalllm-nat-router"
  region  = var.region
  network = google_compute_network.metalllm_vpc.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "metalllm-nat"
  router                             = google_compute_router.nat_router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# Firewall Rules
resource "google_compute_firewall" "allow_internal" {
  name    = "metalllm-allow-internal"
  network = google_compute_network.metalllm_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.0.0.0/16"]
}

resource "google_compute_firewall" "allow_iap_ssh" {
  name    = "metalllm-allow-iap-ssh"
  network = google_compute_network.metalllm_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["35.235.240.0/20"]  # IAP range
}

resource "google_compute_firewall" "deny_all_ingress" {
  name     = "metalllm-deny-all-ingress"
  network  = google_compute_network.metalllm_vpc.name
  priority = 65535

  deny {
    protocol = "all"
  }

  source_ranges = ["0.0.0.0/0"]
}
