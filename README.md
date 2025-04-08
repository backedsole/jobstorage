# jobstorage
Parse and store job descriptions

Start mongodb
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=example
docker run -d --name mongodb-cont --env-file ./mongodb/.env -v jobstorage-mongo:/data/db mongo:8.0.6-noble

Start mondo web interface
ME_CONFIG_MONGODB_URL=mongodb://root:example@mongodb_host_or_ip:27017
ME_CONFIG_BASICAUTH_USERNAME=root
ME_CONFIG_BASICAUTH_PASSWORD=example
docker run -d --name mongo-express-cont -p 9100:8081 --env-file ./mongo-express/.env mongo-express:1.0.2-20-alpine3.19

Set environment
python3 -m venv .venv
source .venv/bin/activate
fastapi==0.115.12
uvicorn==0.34.0
motor==3.7.0
python-dotenv==1.1.0
beautifulsoup4==4.13.3
requests==2.32.3
lxml==5.3.0
tldextract==5.1.3
pip install -r requirements.txt

Run API
uvicorn --app-dir ./src main:app --reload
uvicorn --app-dir ./src --env-file .env main:app --reload
node:23.11.0-bullseye-slim

npm install axios bootstrap