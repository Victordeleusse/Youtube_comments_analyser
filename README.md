# YouTube video(s) general opinion and specific behaviour 
This project was implemented with the aim of training myself in Data/Big Data and Data Engineering. It followed a request from a YouTuber friend of mine who wanted to receive an alert if one or several specific topics were mentioned in any of the comments on its videos, or if a user typed offensive behavior comment.

This project allows the YouTuber to store in a SQL database:

- comments detected by the models as offensive or addressing a specific topic previously defined by the Youtuber;
- the authors of these comments 
- these comments and why they have been detected;
- the date of these publications;

and this for as many videos as desired. 
An account linked to each "bad" user is then incremented to identify the recurrence of certain "harmful" or aggressive viewers.

## Implementation

### 1. GCP x Terraform

Setting up environment variables in the **.env** file: 
	- Google Project + GCP config
	- Model config (If you decide to use Ollama translation model) 

TERRAFORM setup
Loading variables into your current environment: 
```
source .env
``` Then run :
```
	terraform init
	terraform plan
	terraform apply (-auto-approve)
```
		-> A BUCKET is created, for the target channel = bucket_name

### 2. Docker x Airflow

First comment extraction and blobs creation while running 
```
python3 main.py
```




## Classification 
- https://huggingface.co/sileod/deberta-v3-large-tasksource-nli?candidate_labels=steroids%2C+drugs&multi_class=true&text=Amazing+the+video%21+However%2C+in+my+opinion%2C+he+is+no+longer+the+best+French+bodybuilder.+He+has+been+surpassed+by+St%C3%A9phane+Matela.+Despite+this+not+being+the+same+category.

## Offensive
- https://huggingface.co/KoalaAI/OffensiveSpeechDetector?text=In+my+opinion%2C+he+is+no+longer+the+best+French+bodybuilder.+He+has+been+surpassed+by+St%C3%A9phane+Matela.+Despite+this+not+being+the+same+category.

