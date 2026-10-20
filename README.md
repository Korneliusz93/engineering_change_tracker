# Engineering Change Tracker

A Python application for importing engineering change requests from CSV files, validating input data, generating processing reports, and creating issues in Redmine through its API.

The project demonstrates practical skills in Python development, data validation, automated testing, logging, and REST API integration.

## Features

- **CSV Processing** — Imports work requests from semicolon-separated CSV files.
- **Input Validation** — Validates request fields before processing.
- **Duplicate Detection** — Detects duplicate request IDs within the set of valid records.
- **Error Reporting** — Collects invalid records and provides validation error messages.
- **Redmine API Integration** — Creates issues in a configured Redmine project.
- **Logging and Reporting** — Generates processing reports and records application activity.
- **Automated Tests** — Tests application functionality and integration components.

## Tech Stack

- Python 3
- Redmine REST API
- pytest
- Git

Additional libraries and their versions are listed in `requirements.txt`.

## Requirements

- Python 3
- A running Redmine instance
- A Redmine API key
- A Redmine project configured for issue creation

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd engineering_change_tracker
```

Replace `<repository-url>` with the URL of your repository.

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, activate the environment using:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Configuration

### 1. Configure Redmine

Create a project in your Redmine instance and configure the required issue settings.

The application currently expects the following priorities:

- `High`
- `Medium`
- `Low`

Supported status values:

- `open`
- `new`
- `closed`

Configure an appropriate issue type, such as `Feature`, according to your Redmine instance.

**Note:** Priority names, status values, and issue types must match the configuration and identifiers expected by the application and the Redmine API.

### 2. Configure environment variables

Create a `.env` file in the project root:

```dotenv
REDMINE_API_KEY=your_redmine_api_key
```

Replace the placeholder with your actual API key.

Keep credentials out of source control. Ensure `.env` is listed in `.gitignore`.

### 3. Configure the connection

Configure the Redmine instance URL and target project in the application.

For a local Redmine instance, the URL might look like this:

```text
http://localhost:3000/
```

Use the appropriate URL for your environment.

## Input Format

The application expects six semicolon-separated fields per record:

| Field | Description |
|---|---|
| ID | Unique work request identifier |
| Title | Request title |
| Description | Request details |
| Priority | `High`, `Medium`, or `Low` |
| Status | `open`, `new`, or `closed` |
| Contact | Contact email address |

Example input:

```csv
WR-001;Update power supply module;Replace component with revised version;High;open;engineer@example.com
WR-002;Review cooling system;Investigate cooling performance;Medium;new;technician@example.com
```

The example records are illustrative and do not represent real contacts.

## Usage

Run the application from the command line and provide the path to the input CSV file:

```bash
python main.py sample_data/sample_data1.csv
```

Replace `main.py` with the actual application entry-point filename if necessary.

The application:

1. Reads the input CSV file.
2. Validates the structure and fields of each record.
3. Separates valid and invalid requests.
4. Generates and saves a processing report.
5. Submits valid requests to the configured Redmine project.

Check the generated report and application logs to review processing results.

## Testing

Run the automated tests using pytest:

```bash
python -m pytest
```

Integration tests may require a running Redmine instance, a configured test project, and valid API credentials.

Use a dedicated test environment when executing tests that create or modify Redmine issues.

## Limitations and Future Improvements

The current implementation focuses on CSV-based input processing and Redmine issue creation.

Planned improvements include:

- **PostgreSQL Integration** — Persist requests and processing results in an external database.
- **Additional Input Formats** — Support JSON input.
- **Additional Integrations** — Extend the application to support other APIs.
- **Web Application** — Develop a Django-based interface for managing work requests.
- **Improved Operational Reporting** — Provide more detailed reporting of successful and failed API operations.

These improvements are planned and are not part of the current implementation unless explicitly stated otherwise.

## Project Status

The project is under development. Its current focus is input validation, CSV processing, reporting, automated testing, and Redmine API integration.
