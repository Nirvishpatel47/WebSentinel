import os
from pathlib import Path
STRUCTURE = [
    "API/routes.py",
    "API/schemas.py",
    "API/app.py",
    "Scanner/Scan_Engine.py",
    "Scanner/Crawl.py",
    "Scanner/Extract.py",
    "Scanner/Validate.py",
    "Scanner/Browser.py",
    "Scanner/Interactions.py",
    "Scanner/Issues.py",
    "Checks/BrokenLinks.py",
    "Checks/BrokenImages.py",
    "Checks/Forms.py",
    "Checks/Navigation.py",
    "Checks/Responsive.py",
    "Checks/SSL.py",
    "Checks/WordPress.py",
    "Checks/Reachability/HTTPStatus.py",
    "Checks/Reachability/DNS.py",
    "Checks/Reachability/SSL.py",
    "Checks/Reachability/Robots.py",
    "Checks/Reachability/Sitemap.py",
    "Checks/Reachability/Speed.py",
    "Checks/Reachability/HealthCheck.py",
    "Reports/HTML_Report.py",
    "Reports/PDF_Report.py",
    "Reports/JSON_Report.py",
    "Storage/Database.py",
    "Storage/Redis.py",
    "Storage/Artifacts.py",
    "Workers/ScanWorker.py",
    "Workers/Scheduler.py",
    "Integrations/Lighthouse.py",
    "Integrations/WPScan.py",
    "Integrations/PageSpeed.py",
    "Security/Auth.py",
    "Security/Secrets.py",
    "Utils/Logger.py",
    "Utils/Retry.py",
    "Utils/Helpers.py",
    "templates/.gitkeep",
    "static/.gitkeep",
    "tests/.gitkeep",
    "README.md",
    "requirements.txt",
    "docker-compose.yml",
    "Dockerfile",
    ".env.example"
]
def generate_layout(base_directory: str = "."):
    root = Path(base_directory)
    for item in STRUCTURE:
        target_file = root / item
        target_file.parent.mkdir(parents=True, exist_ok=True)
        if not target_file.exists():
            target_file.touch()
if __name__ == "__main__":
    generate_layout()