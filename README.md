# GDGoC VC – Cloud Leaderboard 🚀

Welcome to the **GDGoC VC Cloud Leaderboard**, a web-based project created to track and showcase participants' progress in Google Cloud Skills Boost activities.

This project allows participants to view their achievements, track completed badges, and stay motivated throughout their learning journey.

## ✨ Features

- **Leaderboard:** Displays participant rankings based on completed badges.
- **Automatic Ranking:** Participants are sorted from highest to lowest badge count.
- **Total Participants:** Shows the total number of participants.
- **Total Badges:** Displays the total number of badges completed.
- **Celebration Animation:** Features a congratulatory message and colourful confetti animation when visitors open the page.
- **Simple Interface:** Clean and user-friendly design.

## 🛠️ Technologies Used

- Python
- HTML
- CSS
- JavaScript
- Google Sheets
- GitHub Actions
- GitHub Pages

## 📊 How It Works

1. Participant information and badge details are maintained in Google Sheets.
2. The Python script collects and processes participant data.
3. The completed badge count is calculated for each participant.
4. Participants are sorted according to their badge count.
5. GitHub Actions runs the report-generation workflow.
6. The generated leaderboard is published through GitHub Pages.

## 🏆 Leaderboard Details

The leaderboard displays three main details:

| Rank | Name | Badges Completed |
|---|---|---|
| 1 | Participant Name | 10 |
| 2 | Participant Name | 9 |
| 3 | Participant Name | 8 |

*Note: The above entries are examples. Actual rankings are generated using participant data.*

## 🔄 Updating the Leaderboard

The leaderboard can be updated by running the `generate-report` workflow from the **Actions** tab in the GitHub repository.

After the workflow completes successfully, the generated files are updated.

## 📁 Project Structure

```text
GDGoC-VC-Cloud-Leaderboard/
│
├── .github/
│   └── workflows/
│       └── generate-report.yml
│
├── main.py
├── report.html
├── index.html
├── report.csv
└── report.xlsx
```

## 🎯 Project Objective

The main objective of this project is to encourage students to explore Google Cloud technologies, complete learning activities, earn digital badges, and celebrate their achievements together.

---

**Built with ❤️ for the GDGoC VC Community.**

*Learn • Build • Grow • Celebrate* 🚀
