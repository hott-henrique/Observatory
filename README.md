# Observatory
Observatory is a part of a team-developed project to collect and analyze news.

## Installing
```bash
git clone https://github.com/hott-henrique/Observatory.git
cd Observatory
pip install -r requirements.txt
```

## Running the server
```bash
export JOURNALIST_USER="MONGODB_USER" && export JOURNALIST_PWD="MONGODB_USER_PASSWORD"
uwsgi --http ADDRESS:PORT --master -p NUM_WORKERS -w wsgi:app
```

## Testing
```bash
export API_BASE_URL="http://ADDRESS:PORT"
python3 examples/post-news.py
```
