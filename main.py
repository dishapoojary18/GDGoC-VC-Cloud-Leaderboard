import os
import re
import time
from io import StringIO
from datetime import datetime
from urllib.parse import quote

import pandas as pd
import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
import pytz


# -----------------------------
# CONFIGURATION
# -----------------------------

SHEET_ID = os.getenv("SHEET_ID")

SHEET_NAME = quote("Leaderboard Data")

REQUIRED_BADGES = [
    "The Basics of Google Cloud Compute",
    "Configure Service Accounts and IAM Roles for Google Cloud",
    "Implement Speech and Language Solutions with Pre-trained APIs",
    "Develop AI-Powered Prototypes in Google AI Studio",
    "Analyze Images with the Cloud Vision API",
    "Build a Website on Google Cloud",
    "Create Your First Gemini Enterprise Application",
    "Store, Process, and Manage Data on Google Cloud - Console",
    "Using the Google Cloud Speech API",
    "Explore Generative AI in Agent Platform",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GDGoC-VC-Leaderboard/1.0)"
}


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def normalize(text):
    """Normalize text for badge-name comparison."""
    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_required_badges(source_text):
    """Find matching curriculum badges in a text source."""
    source = normalize(source_text)

    completed = set()

    for badge in REQUIRED_BADGES:
        if normalize(badge) in source:
            completed.add(badge)

    return completed


def get_profile_badges(profile_url):
    """Read badge names from a public Google Skills Boost profile."""

    if not isinstance(profile_url, str) or not profile_url.startswith("http"):
        return set()

    try:
        response = requests.get(
            profile_url,
            headers=HEADERS,
            timeout=6
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        badge_elements = soup.select(
            "span.ql-title-medium.l-mts"
        )

        profile_badges = set()

        for element in badge_elements:
            badge_name = element.get_text(" ", strip=True)

            for required_badge in REQUIRED_BADGES:
                if normalize(badge_name) == normalize(required_badge):
                    profile_badges.add(required_badge)

        return profile_badges

    except requests.RequestException as error:
        print(f"Could not read profile: {profile_url} - {error}")
        return set()

    except Exception as error:
        print(f"Profile processing error: {error}")
        return set()


# -----------------------------
# READ GOOGLE SHEET
# -----------------------------

def read_google_sheet():

    if not SHEET_ID:
        raise ValueError("SHEET_ID secret is missing.")

    sheet_url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
    )

    print("Reading Google Sheet...")

    response = requests.get(
        sheet_url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    data = pd.read_csv(StringIO(response.text))

    data.columns = data.columns.str.strip()

    required_columns = [
        "Participant ID",
        "Display Name",
        "Public Profile URL",
        "Sheet Badge Names",
        "Milestone Completed",
        "GEAR Digital Badges",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in Google Sheet: {missing_columns}"
        )

    data = data.fillna("")

    print(f"Loaded {len(data)} participants.")

    return data


# -----------------------------
# BUILD LEADERBOARD
# -----------------------------

def build_leaderboard(data):

    leaderboard = []

    for _, participant in data.iterrows():

        participant_id = participant["Participant ID"]
        name = participant["Display Name"]
        profile_url = participant["Public Profile URL"]

        sheet_badge_text = participant["Sheet Badge Names"]

        # Badges recorded in Google Sheet
        sheet_badges = find_required_badges(sheet_badge_text)

        # Badges found on public profile
        profile_badges = get_profile_badges(profile_url)

        # Combine unique badges to avoid double-counting
        completed_badges = sheet_badges.union(profile_badges)

        completed_count = len(completed_badges)

        completed_names = [
            badge for badge in REQUIRED_BADGES
            if badge in completed_badges
        ]

        progress = round(
            (completed_count / len(REQUIRED_BADGES)) * 100
        )

        leaderboard.append({
            "Participant ID": participant_id,
            "Display Name": name,
            "Public Profile URL": profile_url,
            "Badges Completed": completed_count,
            "Progress": f"{progress}%",
            "Completed Skill Badges": ", ".join(completed_names),
            "Milestone Completed": participant["Milestone Completed"],
            "GEAR Digital Badges": participant["GEAR Digital Badges"],
        })

        print(
            f"Processed {name}: "
            f"{completed_count}/{len(REQUIRED_BADGES)} badges"
        )

        # Small pause between profile requests
        time.sleep(0.2)

    result = pd.DataFrame(leaderboard)

    result = result.sort_values(
        by=["Badges Completed", "Display Name"],
        ascending=[False, True]
    ).reset_index(drop=True)

    result.insert(
        0,
        "Rank",
        range(1, len(result) + 1)
    )

    return result


# -----------------------------
# GENERATE REPORT FILES
# -----------------------------

def generate_reports(leaderboard):

    timezone = pytz.timezone("Asia/Kolkata")
    current_time = datetime.now(timezone)

    formatted_time = current_time.strftime(
        "%d %B %Y, %I:%M %p"
    )

    # CSV report
    leaderboard.to_csv(
        "report.csv",
        index=False
    )

    # Excel report
    leaderboard.to_excel(
        "report.xlsx",
        index=False
    )

    # HTML table
    table = leaderboard.to_html(
        index=False,
        escape=True,
        classes="leaderboard",
        border=0
    )

    # Use report.html as the HTML template
    environment = Environment(
        loader=FileSystemLoader(".")
    )

    template = environment.get_template("report.html")

    html_output = template.render(
        now=formatted_time,
        time_zone="IST",
        table=table,
        total_participants=len(leaderboard),
        total_badges=len(REQUIRED_BADGES),
    )

    # index.html is the public website entry point
    with open("index.html", "w", encoding="utf-8") as file:
        file.write(html_output)

    print("Reports generated successfully!")


# -----------------------------
# MAIN
# -----------------------------

def main():

    print("Starting GDGoC VC Cloud Leaderboard...")

    data = read_google_sheet()

    leaderboard = build_leaderboard(data)

    generate_reports(leaderboard)

    print("Leaderboard update completed!")


if __name__ == "__main__":
    main()
