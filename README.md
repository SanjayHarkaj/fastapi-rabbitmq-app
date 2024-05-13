## Ticket Sales System Setup Guide

### Prerequisites:
- Python 3.x
- pip (Python package manager)
- RabbitMQ (message broker)
<br /><br />
### Setup Instructions:

#### 1. Clone the Repository:
```bash
git clone <repository_url>
cd fastapi-rabbitmq-app
```
<br/>

#### 2. Create and Activate Virtual Environment:

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux/MacOS:
```bash
python3 -m venv venv
source venv/bin/activate
```
<br/>

#### 3. Install Dependencies:
```bash
pip install -r requirements.txt
```
<br/>

#### 4. Set Configuration:

Ensure to configure your settings in config.py according to your requirements.

<br/>


#### 5. Ensure RabbitMQ is Running:

Make sure RabbitMQ is running on your machine.

<br/>


#### 6. Run Ticketing Service:
```python
uvicorn ticketing_service.main:app --reload
```
<br/>


#### 7. Run Rule Service:
```python
uvicorn rule_service.main:app --port 8001 --reload
```
<br/>

### Usage:

#### Registration:

```bash
curl -X POST http://localhost:8000/register -H "accept: application/json" -H "Content-Type: application/json" -d "{\"username\": \"username\", \"role\": \"standard\", \"password\": \"password\"}"
```
<br/>


#### Login:

```bash
curl -X POST http://localhost:8000/login -d "username=username&password=password"
```
<br/>


#### Requesting Ticketing Link:
```bash
curl -X GET http://localhost:8000/request_for_ticketing_link -H "Authorization: Bearer <token>"
```
<br/>


#### Getting Ticketing Link:
```bash
curl -X GET http://localhost:8000/get_ticketing_link -H "Authorization: Bearer <token>"
```
<br/>


#### Buying Ticket:
```bash
curl -X GET http://localhost:8000/buy_ticket/<access_token> -H "Authorization: Bearer <token>"
```
<br/>

Replace "token" with the actual bearer token received after login and <access_token> received after get_ticket request.
<br />

Note: For Non logged in (guest) users no need to send bearer token.
<br/>

