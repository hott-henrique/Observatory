# Observatory

Observatory is a part of a team-developed project to collect and analyze news.

![image](assets/Architecture.drawio.png)

## Installing

```bash
git clone https://github.com/hott-henrique/Observatory.git
cd Observatory
pip install -r requirements.txt
```

## Running the servers

In order to the system work properly we need two databases: [MongoDB](https://www.mongodb.com/) and [Qdrant](https://qdrant.tech/).

### Setup Qdrant

```bash
python3 -m setup.setup-qdrant
```

### API

```bash
export JOURNALIST_USER="MONGODB_USER"
export JOURNALIST_PWD="MONGODB_USER_PASSWORD"
export QDRANT_URL="QDRANT_CLUSTER_URL"
export QDRANT_TOKEN="QDRANT_API_TOKEN"
uvicorn --host ADDRESS --port PORT app.main:app
```

## Testing

Testing can be performed using a web browser: http://ADDRESS:PORT/docs

