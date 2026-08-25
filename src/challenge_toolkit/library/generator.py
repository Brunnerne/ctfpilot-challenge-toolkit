import os
import sys
from pathlib import Path
from typing import Literal

from .config import CHALLENGE_SCHEMA
from .data import Challenge, Page
from .utils import Utils


class Generator:
    challenge: Challenge
    page: Page
    path: Path

    dir_src: str
    dir_template: str
    dir_files: str
    dir_handout: str
    dir_solvescript: str
    dir_k8s: str

    def __init__(self, challenge: Challenge | None = None, page: Page | None = None):
        if not challenge and not page:
            print("No challenge or page provided")
            sys.exit(1)

        if challenge:
            self.challenge = challenge
            self.path = Utils.get_challenge_dir(challenge.category, challenge.slug)
        if page:
            self.page = page
            self.path = Utils.get_page_dir(page.slug)

        # Directories
        self.dir_src = os.path.join(self.path, "src")
        self.dir_template = os.path.join(self.path, "template")
        self.dir_solvescript = os.path.join(self.path, "solution")

        self.dir_k8s = os.path.join(self.path, "k8s")
        self.dir_files = os.path.join(self.dir_k8s, "files")
        self.dir_handout = os.path.join(self.path, "handout")

    # --- Main functions ---

    def build(self):
        self.src_directory()
        self.solvescript_directory()
        self.files_directory()
        self.handout_directory()

        self.challenge_file(format="yml")
        self.readme_file()
        self.description_file()
        self.version_file()

        if self.challenge.type != "static":
            self.template_directory()
            self.k8s_directory()

            self.dockerfile()
            self.compose_file()

            if self.challenge.type == "shared":
                self.shared_template_file()
            elif self.challenge.type == "instanced":
                self.instanced_template_file()
            else:
                print(
                    f"Challenge type {self.challenge.type} not supported for template generation."
                )

    # --- Helper functions ---

    def check_if_dir_exists(self, dir_path):
        return os.path.exists(dir_path)

    def create_directory_if_not_exists(self, dir_path, dir_name):
        if not self.check_if_dir_exists(dir_path):
            print(f"Creating {dir_name} {dir_path}")
            os.makedirs(dir_path)
            return True
        else:
            print(f"{dir_name} {dir_path} already exists, skipping creation")
            return False

    def write_file(self, file_path, content):
        with open(file_path, "w") as f:
            f.write(content)

    # --- Directories ---

    def chall_directory_exists(self):
        return self.check_if_dir_exists(self.path)

    def chall_directory(self):
        return self.create_directory_if_not_exists(self.path, "challenge directory")

    def src_directory_exists(self):
        return self.check_if_dir_exists(self.dir_src)

    def src_directory(self):
        success = self.create_directory_if_not_exists(self.dir_src, "source directory")

        if success:
            self.write_file(
                os.path.join(self.dir_src, ".gitkeep"),
                """# This file is used to keep the directory in the repository.
# This directory is used to store source files for the challenge.""",
            )

        return success

    def solvescript_directory_exists(self):
        return self.check_if_dir_exists(self.dir_solvescript)

    def solvescript_directory(self):
        success = self.create_directory_if_not_exists(
            self.dir_solvescript, "solution directory"
        )

        if success:
            self.write_file(
                os.path.join(self.dir_solvescript, "README.md"),
                """# Solution
This directory is used to store the solution script for the challenge.
This file should contain the steps to solve the challenge.""",
            )

        return success

    def template_directory_exists(self):
        return self.check_if_dir_exists(self.dir_template)

    def template_directory(self):
        success = self.create_directory_if_not_exists(
            self.dir_template, "template directory"
        )

        if success:
            self.write_file(
                os.path.join(self.dir_template, ".gitkeep"),
                """# This file is used to keep the directory in the repository.
# This directory is used to store templates for the challenge deployment.""",
            )

        return success

    def files_directory_exists(self):
        return self.check_if_dir_exists(self.dir_files)

    def files_directory(self):
        success = self.create_directory_if_not_exists(self.dir_files, "files directory")

        if success:
            self.write_file(
                os.path.join(self.dir_files, ".gitkeep"),
                """# This file is used to keep the directory in the repository.
# This directory is used to store files that are handed out, for the challenge. Use the handout directory for files that are handed out to users and want to be packaged as a zip file.""",
            )

        return success

    def handout_directory_exists(self):
        return self.check_if_dir_exists(self.dir_handout)

    def handout_directory(self):
        success = self.create_directory_if_not_exists(
            self.dir_handout, "handout directory"
        )

        if success:
            self.write_file(
                os.path.join(self.dir_handout, ".gitkeep"),
                """# This file is used to keep the directory in the repository.
# This directory is used to store files that are handed out, for the challenge. The files are automatically zipped and copied to the files directory.""",
            )

    def k8s_directory_exists(self):
        return self.check_if_dir_exists(self.dir_k8s)

    def k8s_directory(self):
        success = self.create_directory_if_not_exists(self.dir_k8s, "k8s directory")

        if success:
            self.write_file(
                os.path.join(self.dir_k8s, ".gitkeep"),
                """# This file is used to keep the directory in the repository.
# This directory is used to store Kubernetes deployment files for the challenge.""",
            )

        return success

    # --- Files ---

    def challenge_file_exists(self):
        # Check yml, yaml and json files
        if self.check_if_dir_exists(os.path.join(self.path, "challenge.yml")):
            return True
        if self.check_if_dir_exists(os.path.join(self.path, "challenge.yaml")):
            return True
        return bool(self.check_if_dir_exists(os.path.join(self.path, "challenge.json")))

    def challenge_file(self, format: Literal["yml", "yaml", "json"] = "yml"):
        if self.challenge_file_exists():
            print("Challenge file already exists!")
            return False

        # Create challenge file
        path = Path(self.path)
        path = path.joinpath(f"challenge.{format}")
        content = self.challenge.str_yml(CHALLENGE_SCHEMA)
        if format == "json":
            content = self.challenge.str_json(CHALLENGE_SCHEMA)

        with open(path, "w") as f:
            f.write(content)
            f.write("\n")

        print(f"File created: {path}")

        return True

    def readme_file_exists(self):
        return self.check_if_dir_exists(os.path.join(self.path, "README.md"))

    def readme_file(self):
        if self.readme_file_exists():
            print("README file already exists!")
            return False

        # Create README file
        path = os.path.join(self.path, "README.md")
        with open(path, "w") as f:
            f.write(f"# {self.challenge.name}\n\n")
            f.write("*Add information about the challenge here*  \n")
            f.write(
                "*This includes all internal documentation about the challenge, such as what it is about and how to run it locally if applicable.  *\n"
            )
            f.write(
                "*The solution should be documented in [solution/README.md](solution/README.md).*"
            )

        print(f"File created: {path}")

        return True

    def description_file_exists(self):
        return self.check_if_dir_exists(os.path.join(self.path, "description.md"))

    def description_file(self):
        if self.description_file_exists():
            print("Description file already exists!")
            return False

        # Create description file
        path = os.path.join(self.path, "description.md")
        with open(path, "w") as f:
            f.write(f"# {self.challenge.name}\n\n")
            f.write(f"**Difficulty:** {self.challenge.difficulty.capitalize()}  \n")
            f.write(f"**Author:** {self.challenge.author}  \n")
            f.write("\n")
            f.write("*Add challenge description here*\n")

        print(f"File created: {path}")

        return True

    def dockerfile_exists(self):
        return self.check_if_dir_exists(os.path.join(self.dir_src, "Dockerfile"))

    def dockerfile(self):
        if self.dockerfile_exists():
            print("Dockerfile already exists!")
            return False

        # Create Dockerfile
        path = os.path.join(self.dir_src, "Dockerfile")
        with open(path, "w") as f:
            f.write(
                f"# Dockerfile for {self.challenge.category} - {self.challenge.name}\n"
            )
            f.write("FROM ubuntu:22.04\n")
            f.write("\n")
            f.write(
                "RUN apt-get update && apt-get upgrade -y && apt-get install -y python3"
            )
            f.write("\n")
            f.write("RUN useradd -m challengeuser\n")
            f.write("\n")
            f.write("USER challengeuser\n")
            f.write("\n")
            f.write(f"EXPOSE {self.challenge.default_port}\n")

        print(f"File created: {path}")

        return True

    def compose_file_exists(self):
        return self.check_if_dir_exists(os.path.join(self.dir_src, "compose.yaml"))

    def compose_file(self):
        if self.compose_file_exists():
            print("Docker Compose file already exists!")
            return False

        # Create Docker Compose file
        path = os.path.join(self.dir_src, "compose.yaml")
        with open(path, "w") as f:
            f.write(
                f"# Docker Compose file for {self.challenge.category} - {self.challenge.name}\n"
            )
            f.write("services:\n")
            f.write(f"  {self.challenge.slug}:\n")
            f.write("    build: .\n")
            f.write("    ports:\n")
            f.write(
                f'      - "{self.challenge.default_port}:{self.challenge.default_port}"\n'
            )

        print(f"File created: {path}")

        return True

    def instanced_template_source_file_exists(self):
        return self.check_if_dir_exists(
            os.path.join(Utils.get_template_dir(), "instanced-web-k8s.yml")
        ) and self.check_if_dir_exists(
            os.path.join(Utils.get_template_dir(), "instanced-tcp-k8s.yml")
        )

    def instanced_template_file_exists(self):
        return self.check_if_dir_exists(os.path.join(self.dir_template, "k8s.yml"))

    def instanced_template_file(self):
        # Check if template directory to write to exists
        if not self.check_if_dir_exists(self.dir_template):
            print("Template directory not found!")
            return False

        # Check if needed template exists
        if not self.instanced_template_source_file_exists():
            print("Instanced k8s template files not found!")
            return False

        # Check if template file already exists
        if self.instanced_template_file_exists():
            print("Template file already exists!")
            return False

        if self.challenge.instanced_type == "web":
            source_file = os.path.join(
                Utils.get_template_dir(), "instanced-web-k8s.yml"
            )
        elif self.challenge.instanced_type == "tcp":
            source_file = os.path.join(
                Utils.get_template_dir(), "instanced-tcp-k8s.yml"
            )
        else:
            print(
                f"Instanced type {self.challenge.instanced_type} is not supported for instanced challenges."
            )
            return False

        output_file = os.path.join(self.dir_template, "k8s.yml")
        with open(source_file, "r") as f, open(output_file, "w") as of:
            of.write(f.read())

        print(f"File created: {output_file}")

        return True

    def shared_template_source_file_exists(self):
        return self.check_if_dir_exists(
            os.path.join(Utils.get_template_dir(), "shared-web-k8s.yml")
        ) and self.check_if_dir_exists(
            os.path.join(Utils.get_template_dir(), "shared-tcp-k8s.yml")
        )

    def shared_template_file_exists(self):
        return self.check_if_dir_exists(os.path.join(self.dir_template, "k8s.yml"))

    def shared_template_file(self):
        # Check if template directory to write to exists
        if not self.check_if_dir_exists(self.dir_template):
            print("Template directory not found!")
            return False

        # Check if needed template exists
        if not self.shared_template_source_file_exists():
            print("Shared k8s template files not found!")
            return False

        # Check if template file already exists
        if self.shared_template_file_exists():
            print("Template file already exists!")
            return False

        if self.challenge.instanced_type == "web":
            source_file = os.path.join(Utils.get_template_dir(), "shared-web-k8s.yml")
        elif self.challenge.instanced_type == "tcp":
            source_file = os.path.join(Utils.get_template_dir(), "shared-tcp-k8s.yml")
        else:
            print(
                f"Instanced type {self.challenge.instanced_type} is not supported for shared challenges."
            )
            return False

        output_file = os.path.join(self.dir_template, "k8s.yml")
        with open(source_file, "r") as f, open(output_file, "w") as of:
            of.write(f.read())

        print(f"File created: {output_file}")

        return True

    def version_file_exists(self):
        return self.check_if_dir_exists(os.path.join(self.path, "version"))

    def version_file(self):
        if self.version_file_exists():
            print("Version file already exists!")
            return False

        # Create VERSION file
        path = os.path.join(self.path, "version")
        with open(path, "w") as f:
            f.write("1")

        print(f"File created: {path}")

        return True
