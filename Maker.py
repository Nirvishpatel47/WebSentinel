# import os
# from pathlib import Path
# STRUCTURE = [
#     "API/routes.py",
#     "API/schemas.py",
#     "API/app.py",
#     "Scanner/Scan_Engine.py",
#     "Scanner/Crawl.py",
#     "Scanner/Extract.py",
#     "Scanner/Validate.py",
#     "Scanner/Browser.py",
#     "Scanner/Interactions.py",
#     "Scanner/Issues.py",
#     "Checks/BrokenLinks.py",
#     "Checks/BrokenImages.py",
#     "Checks/Forms.py",
#     "Checks/Navigation.py",
#     "Checks/Responsive.py",
#     "Checks/SSL.py",
#     "Checks/WordPress.py",
#     "Checks/Reachability/HTTPStatus.py",
#     "Checks/Reachability/DNS.py",
#     "Checks/Reachability/SSL.py",
#     "Checks/Reachability/Robots.py",
#     "Checks/Reachability/Sitemap.py",
#     "Checks/Reachability/Speed.py",
#     "Checks/Reachability/HealthCheck.py",
#     "Reports/HTML_Report.py",
#     "Reports/PDF_Report.py",
#     "Reports/JSON_Report.py",
#     "Storage/Database.py",
#     "Storage/Redis.py",
#     "Storage/Artifacts.py",
#     "Workers/ScanWorker.py",
#     "Workers/Scheduler.py",
#     "Integrations/Lighthouse.py",
#     "Integrations/WPScan.py",
#     "Integrations/PageSpeed.py",
#     "Security/Auth.py",
#     "Security/Secrets.py",
#     "Utils/Logger.py",
#     "Utils/Retry.py",
#     "Utils/Helpers.py",
#     "templates/.gitkeep",
#     "static/.gitkeep",
#     "tests/.gitkeep",
#     "README.md",
#     "requirements.txt",
#     "docker-compose.yml",
#     "Dockerfile",
#     ".env.example"
# ]
# def generate_layout(base_directory: str = "."):
#     root = Path(base_directory)
#     for item in STRUCTURE:
#         target_file = root / item
#         target_file.parent.mkdir(parents=True, exist_ok=True)
#         if not target_file.exists():
#             target_file.touch()
# if __name__ == "__main__":
#     generate_layout()

import os
from pathlib import Path


def create_website_structure():
    # Define the base directory
    base_dir = Path("tests/Website-1")

    # Define the files that sit in the root of Website-1
    root_files = [
        "index.html",
        "about.html",
        "services.html",
        "portfolio.html",
        "blog.html",
        "contact.html",
        "README.md",
    ]

    # Define the nested files inside their respective subdirectories
    subdir_files = [
        "css/style.css",
        "js/app.js",
        "images/logo.png",
        "images/hero.jpg",
        "images/team.jpg",
    ]

    print(f"Creating structure in: {base_dir.resolve()}\n")

    # 1. Create root files
    for file_name in root_files:
        file_path = base_dir / file_name
        # os.makedirs ensures the parent 'Website-1' directory exists
        os.makedirs(file_path.parent, exist_ok=True)
        file_path.touch(exist_ok=True)
        print(f"Created: {file_path}")

    # 2. Create subdirectory files
    for file_path_str in subdir_files:
        file_path = base_dir / file_path_str
        # Create the subdirectories (css, js, images) if they don't exist
        os.makedirs(file_path.parent, exist_ok=True)
        file_path.touch(exist_ok=True)
        print(f"Created: {file_path}")

    print("\nStructure generated successfully!")


if __name__ == "__main__":
    create_website_structure()