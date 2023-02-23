#### Initial setup  
* Create a project  
https://console.cloud.google.com/projectcreate  
* Create a Standard Kubernetes Engine Cluster  
https://console.cloud.google.com/kubernetes/list/overview  
* Install and configure kubectl and gcloud:  
https://cloud.google.com/sdk/docs/install  
https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl#gcloud  
* Connect to the cluster for the project, for example:  
```gcloud container clusters get-credentials birthday-organizer-cluster --region europe-central2 --project birthday-organizer-370909```  
* Select the project
```gcloud config set project birthday-organizer-370909```
#### Building and uploading container images to Google Artifact Repository:  
* Create a Docker repository using this link (changing project name):
  https://console.cloud.google.com/artifacts/create-repo?project=birthday-organizer-370909
* Ensuring that the repository location in the YAML file is updated, execute the following for each submodule (django and postgre):  
```gcloud builds submit --region=us-west2 --config cloudbuild.yaml```  

#### Deploying based on already built images:  
  * Define and upload all secrets one by one:  
    ```kubectl apply -f secrets/<secret>.yaml```  
  * Create peristent volume:  
    ```kubectl apply -f volume/persistent_volume.yaml```  
  * Claim peristent volume:  
    ```kubectl apply -f volume/persistent_volume_claim.yaml```  
  * Apply deployment for the database:  
    ```kubectl apply -f postgre/deploy.yaml```  
  * Expose the database pod by creating a service:  
    ```kubectl apply -f postgre/expose.yaml```  
  * Ensure "birthday_organizer" database exists. Open a terminal to the DB pod (see instructions below) and do:  
    ```su postgres```   
    ```psql -l```  
    If you get an error "role does not exist", create a cluster (15 is simply the version of postgre):  
    ```pg_createcluster 15 main```  
    ```service postgresql restart```  
    If the database doesn't exist, create it:   
    ```psql```  
    ```CREATE DATABASE birthday_organizer;```  
  * Apply deployment for the Django app:  
    ```kubectl apply -f django/deploy.yaml```  
  * Apply deployment for Celery (basically a clone of Django, but with Celery and Redis started).  
    This requires a separate deployment, because it muts be in a single pod to ensure single execution of all tasks.
    ```kubectl apply -f django/deploy.yaml```  
  * Expose the app pod by creating a service:  
    ```kubectl apply -f django/expose.yaml```  
  * Migrate the database by opening a terminal in a django pod and running:  
    ```python3 /var/birthday_organizer/manage.py migrate``` 
  * Get the external IP from the list of services:  
    ```kubectl get service/birthday-organizer-django-service```  

#### Usefull commands:
  * Open terminal to a pod:  
    ```kubectl get pods``` -> Take a note of the pod  
    ```kubectl exec -i -t birthday-organizer-django-96c9f7568-gdx8h -- /bin/bash```  
  * Force update once a new container image is available:
    ```kubectl rollout restart deploy birthday-organizer-django```
