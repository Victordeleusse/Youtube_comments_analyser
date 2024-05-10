# YouTube video(s) specific behaviour 
This project was implemented with the aim of training myself in Data/Big Data and Data Engineering. It followed a request from a YouTuber friend of mine who wanted to receive daily alerts if one or several specific topics were mentioned in any of the comments on its videos, or if a user typed offensive behavior comment.

This project allows the YouTuber to store in a SQL database:

- comments detected by the models and reason why (offensive or addressing a specific topic previously defined by the Youtuber);
- authors of these comments;
- the date of these comments.

This for as many videos as desired.

An account linked to each viewer is then incremented to identify the recurrence of certain behaviour of viewers, and a global report is generated on daily (but it also can be changed) basis to get a global overview of these behaviours on youtube videos comments section.

## Implementation

In a virtual environment, please install requirements.

### 1. GCP x Terraform

Setting up environment variables in the **.env** file: 
	- Google Project + GCP config
	- Model config (If you decide to use Ollama translation model) 

TERRAFORM setup
Loading variables into your current environment: 

```
source .env
``` 

Then run:

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

Then, launching Docker service with an Ollama service and a PostgreSQL instance
```
docker-compose up -d
```

*Airflow requires a database to store its state and configurations. For a simple local installation, you can use SQLite -> many issues arose, particularly regarding simultaneous execution when triggering events, changing the database with the implementation of an SQL client.*

- Create an admin for the service :
```
airflow users create \
    --username victordeleusse \
    --firstname victor \
    --lastname deleusse \
    --role Admin \
    --email victordeleusse@gmail.com \
    --password 1234 
```

- Launch the service after having drop to you dags folder all the necessary files needed to the execution of your functions :

```
airflow db init
airflow scheduler
airflow webserver --port 8080
```


### Hugging Face models used :
- Classification :
https://huggingface.co/sileod/deberta-v3-large-tasksource-nli?candidate_labels=steroids%2C+drugs&multi_class=true&text=Amazing+the+video%21+However%2C+in+my+opinion%2C+he+is+no+longer+the+best+French+bodybuilder.+He+has+been+surpassed+by+St%C3%A9phane+Matela.+Despite+this+not+being+the+same+category.

- Behaviour :
https://huggingface.co/KoalaAI/OffensiveSpeechDetector?text=In+my+opinion%2C+he+is+no+longer+the+best+French+bodybuilder.+He+has+been+surpassed+by+St%C3%A9phane+Matela.+Despite+this+not+being+the+same+category.

Initially, i wanted to use prompt engineering and 


### 3. SQL query and result

After analyzing and classifying comments from different videos, a grouping occurs on tables *bad_comments_table* and *bad_viewers*, and the analysis results are then extracted in PDF format to the path specified in the .env file : **EXTRACT_RESULT_PATH**
