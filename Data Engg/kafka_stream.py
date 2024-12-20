import uuid
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

# Define default arguments for the DAG
default_args = {
    'owner': 'airscholar',  # Indicates the owner of this DAG for metadata purposes
    'start_date': datetime(2023, 9, 3, 10, 00)  # Start date of the DAG; ensure this aligns with your use case
}

# Function to fetch data from the random user API
def get_data():
    import requests

    # Make an API request
    res = requests.get("https://randomuser.me/api/")
    res = res.json()  # Parse the JSON response
    res = res['results'][0]  # Extract the first result from the response

    return res  # Return the result dictionary

# Function to format data into a structured format
def format_data(res):
    data = {}
    location = res['location']  # Extract location details

    # Add formatted data to the dictionary
    data['id'] = uuid.uuid4()  # Generate a unique UUID for the user
    data['first_name'] = res['name']['first']
    data['last_name'] = res['name']['last']
    data['gender'] = res['gender']
    data['address'] = f"{str(location['street']['number'])} {location['street']['name']}, " \
                      f"{location['city']}, {location['state']}, {location['country']}"
    data['post_code'] = location['postcode']
    data['email'] = res['email']
    data['username'] = res['login']['username']
    data['dob'] = res['dob']['date']
    data['registered_date'] = res['registered']['date']
    data['phone'] = res['phone']
    data['picture'] = res['picture']['medium']

    return data  # Return the formatted data

# Function to stream data to a Kafka topic
def stream_data():
    import json
    from kafka import KafkaProducer
    import time
    import logging

    # Create a Kafka producer
    producer = KafkaProducer(bootstrap_servers=['broker:29092'], max_block_ms=5000)  # Adjust broker settings as needed
    curr_time = time.time()  # Capture the current time

    # Continuously stream data for 1 minute
    while True:
        # if time.time() > curr_time + 60:  # Stop streaming after 1 minute
        #     break
        try:
            # Fetch and format data
            res = get_data()
            res = format_data(res)

            # Send data to the Kafka topic
            producer.send('users_created', json.dumps(res).encode('utf-8'))  # Encode the JSON data
        except Exception as e:
            logging.error(f'An error occurred: {e}')  # Log any errors
            continue

# # Define the DAG
# with DAG('user_automation',  # Unique identifier for the DAG
#          default_args=default_args,  # Use the previously defined default arguments
#          schedule_interval='@daily',  # Run the DAG daily
#          catchup=False) as dag:  # Disable backfilling for missed runs

#     # Define a PythonOperator to execute the stream_data function
#     streaming_task = PythonOperator(
#         task_id='stream_data_from_api',  # Unique identifier for this task
#         python_callable=stream_data  # The functi