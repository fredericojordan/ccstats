import os

import requests
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    "Accept": "application/vnd.api+json",
    "Authorization": f"Token token={os.getenv('API_TOKEN')}",
}


def get_rating(repo_id):
    repo_reports = requests.get(
        f"https://api.codeclimate.com/v1/repos/{repo_id}/test_reports", headers=HEADERS
    )

    report_data = repo_reports.json()["data"]

    if len(report_data) == 0:
        return None

    return (
        report_data[0]
        .get("attributes", {})
        .get("rating", {})
        .get("measure", {})
        .get("value")
    )


def get_repos(org_id):
    json_response = requests.get(
        f"https://api.codeclimate.com/v1/orgs/{org_id}/repos",
        headers=HEADERS,
    ).json()
    repos_list = json_response["data"]

    next_page = json_response["links"]["next"]
    while next_page:
        json_response = requests.get(next_page, headers=HEADERS).json()
        repos_list.extend(json_response["data"])
        next_page = json_response["links"].get("next")

    return repos_list


if __name__ == "__main__":
    repos = [
        {
            "id": repo["id"],
            "name": repo["attributes"]["human_name"],
            "coverage_percent": get_rating(repo["id"]),
        }
        for repo in get_repos(os.getenv("ORG_ID"))
    ]
    repos = sorted(
        repos,
        key=lambda x: x["coverage_percent"] if x["coverage_percent"] else 0,
        reverse=True,
    )

    i = 1
    for repo in repos:
        cov = "-"
        if repo["coverage_percent"]:
            cov = "{:.2f}%".format(repo["coverage_percent"])
        print(f"{i}. ({cov}) {repo['name']}")
        i += 1
