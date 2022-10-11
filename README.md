# da-services
Provide one API for get the listing id.      
This program used FastAPI to provide the Post and Get services. It used GraphQL to query data.
![image](https://user-images.githubusercontent.com/75282285/150705586-204a54d4-c5b8-4726-b5b9-1764d6b0ae9e.png)

---
# Docker
## Build an image on Docker
![image](https://user-images.githubusercontent.com/75282285/147958936-9f71fd81-3601-4f94-91bb-b2a93f62fbf4.png)

![image](https://user-images.githubusercontent.com/75282285/147958976-ea9b63d0-a6ea-4c91-bfa6-7ef61420e53a.png)

![image](https://user-images.githubusercontent.com/75282285/147959095-36f762d1-d257-4bd5-ac5e-674ae2639a26.png)

## How to confirm it works OK on Docker
You input the 
  
```json  
{
"name": "Tyndale University",
"postcode": "M2M 3S4",
"address": "3377 Bayview Ave,Toronto",
"region_locality": "Toronto,Ontario"
}
  
```
then you will see this result in the Postman:
![image](https://user-images.githubusercontent.com/75282285/147959279-5653129b-9f31-4ced-bf1f-60370a4cf72d.png)

# Kubernetes
## Build the pod and service on k8s
~~~
kubectl apply -f da-service-dapr.yaml
~~~
![image](https://user-images.githubusercontent.com/75282285/150704964-16a41d2a-1f6a-45de-8616-cdc094e8a42a.png)

![image](https://user-images.githubusercontent.com/75282285/150704975-225e1576-259f-4b5d-b5d3-931dabb20110.png)

# Dapr

![image](https://user-images.githubusercontent.com/75282285/150705135-a93a0283-0ae0-43fb-b699-752aba3a2ccb.png)

# How to test it can work on K8S + Dapr

~~~
kubectl port-forward da-services-86978f9578-pkhsz   8082:3500
~~~

![image](https://user-images.githubusercontent.com/75282285/150705052-bb8d0d6a-9faf-478f-9a8c-41ca72cf02a6.png)

~~~
 curl http:// 127.0.0.1:8082/v1.0/invoke/da-services/method/
~~~
![image](https://user-images.githubusercontent.com/75282285/150705088-c6c15b1f-352e-4bca-b8be-22ec9531a6fc.png)


~~~
http://127.0.0.1:8082/v1.0/invoke/da-services/method/listings/matching/
~~~
We can test it with Postman.
![image](https://user-images.githubusercontent.com/75282285/150705104-245ea9f1-d2cc-4404-8fab-1220175d465c.png)

# Use GreaphQL to query in graphql.py and listing_match.py
Use `graphql_df = graphql.listingsearch(**search_params) ` to query.
~~~
def match_graphql(name, near):
    """
    Search the listing id info through region_locality.
    :param name:(str).
    :param near:(str) one of the postcode, location, region_locality
    :return result_df:(df) columns such as ['score', 'id', 'name', 'otherNames', 'street', 'locality', 'region',
                               'postalCode', 'primaryLink', 'email', 'category', 'denomination', 'type']
    :return top_score:(int) If graphql find nothing, it will return 0.
    :return result_num:(int) If graphql find nothing, it will return 0.
    """
    result_df = pd.DataFrame(columns=['score', 'id', 'name', 'otherNames', 'street', 'locality', 'region',
                                      'postalCode', 'primaryLink', 'email', 'category', 'denomination', 'type'])
    search_params = {"keywords": name, "near": near}
    graphql_df = graphql.listingsearch(**search_params)  # df or list
    if len(graphql_df) > 0:
        top_score = graphql_df['score'].max()
        result_num = len(graphql_df)
        result_df = graphql_df.sort_values('score', ascending=False)
        result_df.reset_index(drop=True, inplace=True)
        return result_df, top_score, result_num
    else:
        return result_df, 0, 0
~~~


