# Output important information

output "control_node_name" {
  description = "Control node instance name"
  value       = google_compute_instance.control_node.name
}

output "control_node_internal_ip" {
  description = "Control node internal IP"
  value       = google_compute_instance.control_node.network_interface[0].network_ip
}

output "ssh_command" {
  description = "SSH command to access control node"
  value       = "gcloud compute ssh ${google_compute_instance.control_node.name} --tunnel-through-iap --zone=${var.zone}"
}

output "target_instances" {
  description = "All target instance names and IPs"
  value = {
    ollama = var.enable_gpu && length(google_compute_instance.ollama_target) > 0 ? {
      name = google_compute_instance.ollama_target[0].name
      ip   = google_compute_instance.ollama_target[0].network_interface[0].network_ip
    } : null
    vllm = var.enable_gpu && length(google_compute_instance.vllm_target) > 0 ? {
      name = google_compute_instance.vllm_target[0].name
      ip   = google_compute_instance.vllm_target[0].network_interface[0].network_ip
    } : null
    qdrant = {
      name = google_compute_instance.qdrant_target.name
      ip   = google_compute_instance.qdrant_target.network_interface[0].network_ip
    }
    langchain = {
      name = google_compute_instance.langchain_target.name
      ip   = google_compute_instance.langchain_target.network_interface[0].network_ip
    }
    mlflow = {
      name = google_compute_instance.mlflow_target.name
      ip   = google_compute_instance.mlflow_target.network_interface[0].network_ip
    }
  }
}

output "start_all_command" {
  description = "Command to start all instances"
  value       = "gcloud compute instances start ${google_compute_instance.control_node.name} ${join(" ", [for inst in concat(var.enable_gpu ? google_compute_instance.ollama_target : [], var.enable_gpu ? google_compute_instance.vllm_target : []) : inst.name])} ${google_compute_instance.qdrant_target.name} ${google_compute_instance.langchain_target.name} ${google_compute_instance.mlflow_target.name} --zone=${var.zone}"
}

output "stop_all_command" {
  description = "Command to stop all instances"
  value       = "gcloud compute instances stop ${google_compute_instance.control_node.name} ${join(" ", [for inst in concat(var.enable_gpu ? google_compute_instance.ollama_target : [], var.enable_gpu ? google_compute_instance.vllm_target : []) : inst.name])} ${google_compute_instance.qdrant_target.name} ${google_compute_instance.langchain_target.name} ${google_compute_instance.mlflow_target.name} --zone=${var.zone}"
}
