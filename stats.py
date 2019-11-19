import asyncio
import os

import aiohttp
import requests
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    "Accept": "application/vnd.api+json",
    "Authorization": f"Token token={os.getenv('API_TOKEN')}",
}


def get_org_repos(org_id):
    json_response = requests.get(
        f"https://api.codeclimate.com/v1/orgs/{org_id}/repos", headers=HEADERS
    ).json()
    repos_list = json_response["data"]

    next_page = json_response["links"]["next"]
    while next_page:
        json_response = requests.get(next_page, headers=HEADERS).json()
        repos_list.extend(json_response["data"])
        next_page = json_response["links"].get("next")

    return repos_list


def print_sorted_list(repo_list):
    i = 1
    for repo in repo_list:
        cov = "-"
        if repo["coverage_percent"]:
            cov = "{:.2f}%".format(repo["coverage_percent"])
        print(f"{i}. ({cov}) {repo['repo']['attributes']['human_name']}")
        i += 1


def parse_test_reports_coverage(test_reports):
    parsed_reports = []

    for test_report in test_reports:
        if len(test_report["test_reports"]["data"]) == 0:
            coverage = None
        else:
            coverage = (
                test_report["test_reports"]["data"][0]
                    .get("attributes", {})
                    .get("rating", {})
                    .get("measure", {})
                    .get("value")
            )
        parsed_reports.append({**test_report, "coverage_percent": coverage})

    return parsed_reports


async def get_test_reports(session, repo_data):
    url = f"https://api.codeclimate.com/v1/repos/{repo_data['id']}/test_reports"
    async with session.get(url, headers=HEADERS) as response:
        return {"repo": repo_data, "test_reports": await response.json()}


async def print_test_coverage_async(org_repositories_data):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for repo_data in org_repositories_data:
            tasks.append(get_test_reports(session, repo_data))
        test_reports = await asyncio.gather(*tasks)

        parsed_test_reports = parse_test_reports_coverage(test_reports)

        repos_sorted_by_coverage = sorted(
            parsed_test_reports,
            key=lambda x: x["coverage_percent"] if x["coverage_percent"] else 0,
            reverse=True,
        )

        print_sorted_list(repos_sorted_by_coverage)


if __name__ == "__main__":
    org_repositories = get_org_repos(os.getenv("ORG_ID"))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(print_test_coverage_async(org_repositories))
