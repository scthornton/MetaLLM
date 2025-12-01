variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "us-central1-a"
}

variable "owner_email" {
  description = "Lab owner email for IAP access"
  type        = string
}

variable "use_spot_instances" {
  description = "Use preemptible instances"
  type        = bool
  default     = true
}

variable "enable_gpu" {
  description = "Enable GPU instances"
  type        = bool
  default     = true
}
