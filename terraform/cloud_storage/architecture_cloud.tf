variable "PROJECT_ID" {}
variable "REGION" {}
variable "NAME" {}
variable "PASSWORD" {}
variable "KEY_GCP_PATH" {}

provider "google" {
  credentials = file(var.KEY_GCP_PATH)
  project     = var.PROJECT_ID
  region      = var.REGION
}

resource "google_storage_bucket" "my_bucket" {
  name     = var.NAME
  location = var.REGION
}