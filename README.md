# ab-kri-middleware

### An exploratory middleware service allowing external api interaction via KRIs 

## Prerequisites
Uses [Python 3.8](https://www.python.org/downloads/release/python-380/)

```bash
# install using homebrew
brew install python@3.8
```

## Create virtual environment
```bash
# with python3.8 installed
python3.8 -m venv venv

# activate the virtual environment
source ./venv/bin/activate
```

## Requirments
```bash
# for all requirements
(venv) pip install --upgrade -r requirements.txt -r dev-requirements.txt -r test-requirements.txt --trusted-host pypi.python.org
```


## Use
```bash
# supply the service name and the configuration file
(venv) python app/services/simple_fetch/main.py -f app/services/simple_fetch/config.yml -s galaxy
```
