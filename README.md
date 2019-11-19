# CodeClimate Organization Statistics

Given an GitHub organization within CodeClimate, fetch all their tracked repositories and sorted them by test coverage.

## Requirements

- Python 3.6 or higher

## Installing

Install the required packages with:

```shell
pip install -r requirements.txt
```

Also create a `.env` file with your own values (without the quotation marks):

```shell
API_TOKEN="Your CodeClimate API Token"
ORG_ID="Your CodeClimate Organization ID"
```

## Running

Just run:

```shell
python stats.py
```
