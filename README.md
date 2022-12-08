#### Initial setup  
* Create a project  
https://console.cloud.google.com/projectcreate  
* Create a Kubernetes Engine Cluster  
https://console.cloud.google.com/kubernetes/list/overview  
* Install and configure kubectl and gcloud:  
https://cloud.google.com/sdk/docs/install  
https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl#gcloud  
* Connect to the cluster for the project, for example:  
```gcloud container clusters get-credentials birthday-organizer-cluster --region europe-central2 --project birthday-organizer-370909```  

#### Building and uploading container images to Google Artifact Repository:  
*  Ensuring that the repository location in the YAML file is updated, execute the following for each submodule (django and postgre):  
```gcloud builds submit --region=us-west2 --config cloudbuild.yaml```  

#### Deploying based on already built images:  
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
    If doesn't exist, create it:  
    ```psql```  
    ```CREATE DATABASE birthday_organizer;```  
  * Apply deployment for the Django app:  
    ```kubectl apply -f django/deploy.yaml```  
  * Expose the app pod by creating a service:  
    ```kubectl apply -f django/expose.yaml```  
  * Get the external IP from the list of services:  
    ```kubectl get service/birthday-organizer-django-service```  

#### Usefull commands:
  * Open terminal to a pod:  
    ```kubectl get pods``` -> Take a note of the pod  
    ```kubectl exec -i -t birthday-organizer-django-69f5c67b88-8vc7z -- /bin/bash```  

TODO: Add apache  
      Test deployment on a fresh cluster to verify DB reinitialization  
      Hide secrets (Django key and DB credentials)  
      Take the actual code and include it  
      Refactor the actual code  
      Include email alerts and some kind of Google Authentication  