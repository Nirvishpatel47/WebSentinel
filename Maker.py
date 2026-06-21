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

# import os
# from pathlib import Path


# def create_website_structure():
#     # Define the base directory
#     base_dir = Path("tests/Website-1")

#     # Define the files that sit in the root of Website-1
#     root_files = [
#         "index.html",
#         "about.html",
#         "services.html",
#         "portfolio.html",
#         "blog.html",
#         "contact.html",
#         "README.md",
#     ]

#     # Define the nested files inside their respective subdirectories
#     subdir_files = [
#         "css/style.css",
#         "js/app.js",
#         "images/logo.png",
#         "images/hero.jpg",
#         "images/team.jpg",
#     ]

#     print(f"Creating structure in: {base_dir.resolve()}\n")

#     # 1. Create root files
#     for file_name in root_files:
#         file_path = base_dir / file_name
#         # os.makedirs ensures the parent 'Website-1' directory exists
#         os.makedirs(file_path.parent, exist_ok=True)
#         file_path.touch(exist_ok=True)
#         print(f"Created: {file_path}")

#     # 2. Create subdirectory files
#     for file_path_str in subdir_files:
#         file_path = base_dir / file_path_str
#         # Create the subdirectories (css, js, images) if they don't exist
#         os.makedirs(file_path.parent, exist_ok=True)
#         file_path.touch(exist_ok=True)
#         print(f"Created: {file_path}")

#     print("\nStructure generated successfully!")


# if __name__ == "__main__":
#     create_website_structure()

# import os
# from pathlib import Path

# def generate_website_structure():
#     # Define the base directory
#     base_dir = Path("tests/Website-3")
    
#     # Define the structure: directories and files
#     structure = {
#         "directories": ["css", "js"],
#         "files": [
#             "index.html",
#             "services.html",
#             "pricing.html",
#             "faq.html",
#             "about.html",
#             "contact.html",
#             "css/style.css",
#             "js/app.js",
#             "README.md"
#         ]
#     }

#     # Create base directory
#     base_dir.mkdir(exist_ok=True)
#     print(f"Created directory: {base_dir}")

#     # Create subdirectories
#     for folder in structure["directories"]:
#         (base_dir / folder).mkdir(exist_ok=True)
#         print(f"Created directory: {base_dir / folder}")

#     # Create files
#     for file_path in structure["files"]:
#         full_path = base_dir / file_path
#         full_path.touch(exist_ok=True)
#         print(f"Created file: {full_path}")

# if __name__ == "__main__":
#     generate_website_structure()

# import os
# from pathlib import Path

# def generate_website_structure():
#     base_dir = Path("tests/Website-1")
    
#     # Define directories and files
#     directories = ["css", "js", "images"]
#     files = [
#         "index.html",
#         "about.html",
#         "services.html",
#         "portfolio.html",
#         "blog.html",
#         "contact.html",
#         "css/style.css",
#         "js/app.js",
#         "images/logo.png",
#         "images/hero.jpg",
#         "images/team.jpg",
#         "README.md"
#     ]

#     # Create directories
#     base_dir.mkdir(exist_ok=True)
#     for folder in directories:
#         (base_dir / folder).mkdir(exist_ok=True)

#     # Create files
#     for file_path in files:
#         full_path = base_dir / file_path
#         full_path.touch(exist_ok=True)
        
#     print(f"Successfully created structure in: {base_dir.resolve()}")

# if __name__ == "__main__":
#     generate_website_structure()

# import os
# from pathlib import Path

# def generate_website_structure():
#     base_dir = Path("tests/Website-2")
    
#     # Define directories to create
#     directories = ["css", "js", "images"]
    
#     # Define files to create
#     files = [
#         "index.html",
#         "about.html",
#         "gallery.html",
#         "services.html",
#         "contact.html",
#         "css/style.css",
#         "js/app.js",
#         "images/logo.png",
#         "images/hero.jpg",
#         "images/team.jpg",
#         "images/gallery1.jpg",
#         "images/gallery2.jpg",
#         "images/gallery3.jpg",
#         "README.md"
#     ]

#     # Create root directory and subdirectories
#     base_dir.mkdir(exist_ok=True)
#     for folder in directories:
#         (base_dir / folder).mkdir(exist_ok=True)

#     # Create all files
#     for file_path in files:
#         full_path = base_dir / file_path
#         full_path.touch(exist_ok=True)
        
#     print(f"Structure for '{base_dir}' created successfully.")

# if __name__ == "__main__":
#     generate_website_structure()

import os

def create_website_structure():
    base_dir = "tests/Website-4"
    
    # Define the files and their content
    file_contents = {
        "index.html": "<!DOCTYPE html>\n<html>\n<head><link rel='stylesheet' href='styles.css'></head>\n<body><h1>Test Scenarios</h1><script src='scripts.js'></script></body>\n</html>",
        "contact.html": "<!DOCTYPE html>\n<html>\n<body><form id='contactForm'></form><script src='scripts.js'></script></body>\n</html>",
        "quote.html": "<!DOCTYPE html>\n<html>\n<body><form id='quoteForm'></form></body>\n</html>",
        "newsletter.html": "<!DOCTYPE html>\n<html>\n<body><form id='newsForm'></form></body>\n</html>",
        "feedback.html": "<!DOCTYPE html>\n<html>\n<body><form id='feedForm'></form><script src='scripts.js'></script></body>\n</html>",
        "styles.css": "/* Modern responsive CSS */\n.card-grid { display: grid; gap: 20px; }",
        "scripts.js": "// All JavaScript logic\nconsole.log('Test suite loaded');",
        "README.md": "# Test Suite\nGround truth documentation."
    }

    # Create the base directory
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"Created directory: {base_dir}")

    # Create files inside the directory
    for filename, content in file_contents.items():
        file_path = os.path.join(base_dir, filename)
        with open(file_path, "w") as f:
            f.write(content)
        print(f"Created file: {file_path}")

if __name__ == "__main__":
    create_website_structure()