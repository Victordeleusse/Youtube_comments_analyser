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

resource "google_sql_database_instance" "default" {
  name             = "youtube-comments-instance"
  database_version = "POSTGRES_12"
  region           = var.REGION

  settings {
    tier = "db-f1-micro"
  }
}

resource "google_sql_database" "default" {
  name     = var.NAME
  instance = google_sql_database_instance.default.name
}

resource "google_sql_user" "default" {
  name     = "youtube_user"
  instance = google_sql_database_instance.default.name
  password = var.PASSWORD
}