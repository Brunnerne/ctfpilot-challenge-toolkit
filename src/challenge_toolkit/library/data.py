import json as _json
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml as _yaml

from .config import (
    CATEGORIES,
    CHALL_TYPES,
    DEFAULT,
    DIFFICULTIES,
    FLAG_FORMAT,
    INSTANCED_TYPES,
    TAG_FORMAT,
)
from .utils import Utils


@dataclass
class DockerfileLocation:
    location: str
    context: str
    identifier: str | None = None

    def __post_init__(self):
        self.validate_location()
        self.validate_context()
        self.validate_identifier()

    def validate_location(self):
        if not re.match(r"^[a-zA-Z0-9-_/\.]+$", self.location):
            print("Dockerfile location must be a valid file path to a Dockerfile.")
            raise ValueError(
                "Dockerfile location must be a valid file path to a Dockerfile."
            )

    def validate_context(self):
        if not re.match(r"^[a-zA-Z0-9-_/\.]+$", self.context):
            print("Dockerfile context must be a valid file path.")
            raise ValueError("Dockerfile context must be a valid file path.")

    def validate_identifier(self):
        self.identifier = Utils.slugify(self.identifier) or None

        if self.identifier is not None and not Utils.validate_length(
            self.identifier, 1, 50, "identifier"
        ):
            raise ValueError("Identifier must be between 1 and 50 characters.")


@dataclass
class ChallengeFlag:
    flag: str
    case_sensitive: bool = False

    def __post_init__(self):
        if not Utils.validate_length(self.flag, 1, 1000, "flag"):
            raise ValueError("Flag must be between 1 and 1000 characters.")

        self.flag = self.flag.strip().replace("\n", "").replace("\r", "")
        if not re.match(FLAG_FORMAT, self.flag):
            print("Flag must be in the format: " + FLAG_FORMAT)
            raise ValueError(
                'The flag "' + self.flag + '" must be in the format: ' + FLAG_FORMAT
            )

    def to_dict(self):
        return {"flag": self.flag, "case_sensitive": self.case_sensitive}


@dataclass
class Challenge:
    name: str
    slug: str
    author: str
    category: str
    difficulty: str
    type: str
    tags: list[str] = field(default_factory=list)
    instanced_type: str = DEFAULT["instanced_type"]
    instanced_name: str | None = DEFAULT["instanced_name"]
    instanced_subdomains: list[str] = field(default_factory=list)
    connection: str | None = DEFAULT["connection"]
    flag: list[ChallengeFlag] | None = None
    enabled: bool = DEFAULT["enabled"]
    points: int = DEFAULT["points"]
    decay: int = DEFAULT["decay"]
    min_points: int = DEFAULT["min_points"]
    description_location: str = DEFAULT["description_location"]
    handout_dir: str = DEFAULT["handout_dir"]
    dockerfile_locations: list[DockerfileLocation] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)

    def __post_init__(self):
        # Run validations
        self.validate_name()
        self.validate_slug()
        self.validate_author()
        self.validate_category()
        self.validate_difficulty()
        self.validate_type()
        self.validate_tags()
        self.validate_instanced_type()
        self.validate_instanced_name()
        self.validate_instanced_subdomains()
        self.validate_connection()
        self.validate_flag()
        self.validate_points()
        self.validate_decay()
        self.validate_min_points()
        self.validate_description_location()
        self.validate_handout_dir()

        if self.instanced_type == "tcp":
            self.default_port = 1337
        elif self.instanced_type == "web":
            self.default_port = 80

    def validate_name(self):
        if not Utils.validate_length(self.name, 1, 50, "name"):
            raise ValueError("Name must be between 1 and 50 characters.")

    def validate_slug(self):
        self.slug = Utils.slugify(self.slug) or ""
        if not Utils.validate_length(self.slug, 1, 50, "slug"):
            raise ValueError("Slug must be between 1 and 50 characters.")

    def validate_author(self):
        if not Utils.validate_length(self.author, 1, 100, "author"):
            raise ValueError("Author must be between 1 and 100 characters.")

    def validate_category(self):
        if not Utils.validate_length(self.category, 1, 50, "category"):
            raise ValueError("Category must be between 1 and 50 characters.")

        if self.category not in CATEGORIES:
            print("Category must be one of the following: " + ", ".join(CATEGORIES))
            raise ValueError(
                "Invalid category provided. Category must be one of the following: "
                + ", ".join(CATEGORIES)
            )

    def validate_difficulty(self):
        if self.difficulty is None:
            print("Difficulty must be provided.")
            raise ValueError("Difficulty must be provided.")

        self.difficulty = self.difficulty.lower()
        if self.difficulty not in DIFFICULTIES:
            print("Difficulty must be one of the following: " + ", ".join(DIFFICULTIES))
            raise ValueError(
                "Invalid difficulty provided. Difficulty must be one of the following: "
                + ", ".join(DIFFICULTIES)
            )

    def validate_type(self):
        if self.type is None:
            print("Type must be provided.")
            raise ValueError("Type must be provided.")

        self.type = self.type.lower()
        if self.type not in CHALL_TYPES:
            print("Type must be one of the following: " + ", ".join(CHALL_TYPES))
            raise ValueError(
                "Invalid type provided. Type must be one of the following: "
                + ", ".join(CHALL_TYPES)
            )

    def validate_tags(self):
        if not isinstance(self.tags, list):
            print("Tags must be a list of strings.")
            raise TypeError("Tags must be a list of strings.")

        for tag in self.tags:
            if not re.match(TAG_FORMAT, tag):
                print(f"Tag '{tag}' does not match the required format: {TAG_FORMAT}")
                raise ValueError(
                    f"Tag '{tag}' does not match the required format: {TAG_FORMAT}"
                )

    def validate_instanced_type(self):
        self.instanced_type = self.instanced_type.lower()
        if self.instanced_type not in INSTANCED_TYPES:
            print(
                "Instanced type must be one of the following: "
                + ", ".join(INSTANCED_TYPES)
            )
            raise ValueError(
                "Invalid instanced type provided. Instanced type must be one of the following: "
                + ", ".join(INSTANCED_TYPES)
            )

    def validate_instanced_name(self):
        if self.instanced_name is None:
            return

        self.instanced_name = Utils.slugify(self.instanced_name)
        if not Utils.validate_length(self.instanced_name, 1, 50, "instanced_name"):
            raise ValueError("Instanced name must be between 1 and 50 characters.")

    def validate_instanced_subdomains(self):
        if not isinstance(self.instanced_subdomains, list):
            print("Instanced subdomains must be a list of strings.")
            raise TypeError("Instanced subdomains must be a list of strings.")

        if len(self.instanced_subdomains) > 5:
            print("Instanced subdomains must not exceed 5 items.")
            raise ValueError("Instanced subdomains must not exceed 5 items.")

        for subdomain in self.instanced_subdomains:
            if not re.match(r"^((web|tcp):)?[a-z0-9-]+$", subdomain):
                print(
                    f"Subdomain '{subdomain}' does not match the required format: ^((web|tcp):)?[a-z0-9-]+$"
                )
                raise ValueError(
                    f"Subdomain '{subdomain}' does not match the required format: ^((web|tcp):)?[a-z0-9-]+$"
                )

            if len(subdomain) > 10:
                print(
                    f"Subdomain '{subdomain}' exceeds the maximum length of 10 characters."
                )
                raise ValueError(
                    f"Subdomain '{subdomain}' exceeds the maximum length of 10 characters."
                )

    def validate_connection(self):
        if self.connection is None:
            return

        if not isinstance(self.connection, str):
            print("Connection must be a string or None.")
            raise TypeError("Connection must be a string or None.")

        # Max length of 255
        if not Utils.validate_length(self.connection, 1, 255, "connection"):
            raise ValueError("Connection string must be between 1 and 255 characters.")

    def validate_flag(self):
        if isinstance(self.flag, list):
            clean_flags = []
            for f in self.flag:
                if isinstance(f, ChallengeFlag):
                    clean_flags.append(f)
                elif isinstance(f, str):
                    clean_flags.append(ChallengeFlag(f))
                elif isinstance(f, dict):
                    if "flag" not in f or not isinstance(f["flag"], str):
                        raise ValueError(
                            "Each flag dictionary must contain a 'flag' key with a string value."
                        )
                    case_sensitive = f.get("case_sensitive", False)
                    clean_flags.append(ChallengeFlag(f["flag"], case_sensitive))
            if not clean_flags:
                raise ValueError("No valid flags provided in list.")
            self.flag = clean_flags
        elif isinstance(self.flag, str):
            self.flag = [ChallengeFlag(self.flag)]
        elif isinstance(self.flag, ChallengeFlag):
            self.flag = [self.flag]
        else:
            self.flag = None

    def validate_points(self):
        if self.points is not None and (self.points < 1 or self.points > 10000):
            print("Points must be between 1 and 10000.")
            raise ValueError("Points must be between 1 and 10000.")

    def validate_decay(self):
        if self.decay is not None and (self.decay < 0 or self.decay > 10000):
            print("Decay must be between 0 and 10000.")
            raise ValueError("Decay must be between 0 and 10000.")

    def validate_min_points(self):
        if self.min_points and (self.min_points < 1 or self.min_points > 1000):
            print("Minimum points must be between 1 and 1000.")
            raise ValueError("Minimum points must be between 1 and 1000.")

    def validate_description_location(self):
        if not re.match(r"^[a-zA-Z0-9-_/]+.md$", self.description_location):
            print("Description location must be a valid file path to a Markdown file.")
            raise ValueError(
                "Description location must be a valid file path to a Markdown file."
            )

    def validate_handout_dir(self):
        if not re.match(r"^[a-zA-Z0-9-_/]+$", self.handout_dir):
            print("Handout directory must be a valid file path.")
            raise ValueError("Handout directory must be a valid file path.")

    def add_dockerfile_location(self, locations: list[DockerfileLocation]):
        self.dockerfile_locations.extend(locations)

    def add_prerequisite(self, prerequisite: str | None):
        prerequisite = Utils.slugify(prerequisite)

        if prerequisite is None:
            print("Prerequisite must be provided.")
            raise ValueError("Prerequisite must be provided.")

        if not Utils.validate_length(prerequisite, 1, 50, "prerequisite"):
            raise ValueError("Prerequisite must be between 1 and 50 characters.")

        if prerequisite in self.prerequisites:
            print(f"Prerequisite {prerequisite} already exists.")
            raise ValueError("Prerequisite already exists.")

        self.prerequisites.append(prerequisite)

    def get_description(self):
        file = self.get_path().joinpath(self.description_location)

        if not file.exists():
            return ""

        with open(file, "r") as f:
            return f.read()

    def get_version(self):
        file = self.get_path().joinpath("version")

        if not file.exists():
            return 0

        with open(file, "r") as f:
            return int(f.read())

    def save_version(self, version: int):
        file = self.get_path().joinpath("version")

        with open(file, "w") as f:
            f.write(str(version))

    def get_path(self):
        return Utils.get_challenge_dir(self.category, self.slug)

    def generate_dict(self, schema_location: str):
        # Use a local variable for flag to avoid modifying self.flag
        flag = [f.to_dict() for f in self.flag] if self.flag else None
        tags = self.tags if self.tags else []

        data = {
            "$schema": schema_location,
            "enabled": self.enabled,
            "name": self.name,
            "slug": self.slug,
            "author": self.author,
            "category": self.category,
            "difficulty": self.difficulty,
            "tags": tags,
            "type": self.type,
            "instanced_type": self.instanced_type,
            "instanced_name": self.instanced_name,
            "instanced_subdomains": self.instanced_subdomains,
            "connection": self.connection,
            "flag": flag,
            "description_location": self.description_location,
            "handout_dir": self.handout_dir,
        }
        if self.points:
            data["points"] = self.points
        if self.decay:
            data["decay"] = self.decay
        if self.min_points:
            data["min_points"] = self.min_points
        if self.dockerfile_locations:
            data["dockerfile_locations"] = [
                {
                    "location": loc.location,
                    "context": loc.context,
                    "identifier": loc.identifier,
                }
                for loc in self.dockerfile_locations
            ]
        if self.prerequisites:
            data["prerequisites"] = self.prerequisites
        return data

    def str_yml(self, schema_location: str):
        data = self.generate_dict(schema_location)
        # Remove $schema from dict for yaml, as it will be added as a comment
        schema = data.pop("$schema", None)
        yml_str = f"# yaml-language-server: $schema={schema}\n\n"
        yml_str += _yaml.dump(data, sort_keys=False, allow_unicode=True)
        return yml_str

    def str_json(self, schema_location: str):
        data = self.generate_dict(schema_location)
        return _json.dumps(data, indent=2)

    def __str__(self):
        return self.str_yml("-")

    @staticmethod
    def load_from_yaml(yml: dict):
        challenge = Challenge(
            enabled=yml.get("enabled", True),
            name=yml.get("name", None),
            slug=yml.get("slug", None),
            author=yml.get("author", None),
            category=yml.get("category", None),
            difficulty=yml.get("difficulty", None),
            type=yml.get("type", None),
            tags=yml.get("tags", []),
            instanced_type=yml.get("instanced_type", "none"),
            instanced_name=yml.get("instanced_name", None),
            instanced_subdomains=yml.get("instanced_subdomains", []),
            connection=yml.get("connection", None),
            flag=yml.get("flag", None),
            points=yml.get("points", None),
            decay=yml.get("decay", None),
            min_points=yml.get("min_points", None),
            description_location=yml.get("description_location", None),
            handout_dir=yml.get("handout_dir", None),
        )

        dockerfile_locations = yml.get("dockerfile_locations", [])
        for location in dockerfile_locations:
            challenge.add_dockerfile_location(
                [
                    DockerfileLocation(
                        location.get("location", "src/Dockerfile"),
                        location.get("context", "src/"),
                        location.get("identifier", None),
                    )
                ]
            )

        prerequisites = yml.get("prerequisites", [])
        for prerequisite in prerequisites:
            challenge.add_prerequisite(prerequisite)

        return challenge

    @staticmethod
    def load_from_json(json_data: dict):
        challenge = Challenge(
            enabled=json_data.get("enabled", True),
            name=json_data.get("name", None),
            slug=json_data.get("slug", None),
            author=json_data.get("author", None),
            category=json_data.get("category", None),
            difficulty=json_data.get("difficulty", None),
            tags=json_data.get("tags", []),
            type=json_data.get("type", None),
            instanced_type=json_data.get("instanced_type", "none"),
            instanced_name=json_data.get("instanced_name", None),
            instanced_subdomains=json_data.get("instanced_subdomains", []),
            connection=json_data.get("connection", None),
            flag=json_data.get("flag", None),
            points=json_data.get("points", None),
            decay=json_data.get("decay", None),
            min_points=json_data.get("min_points", None),
            description_location=json_data.get("description_location", None),
            handout_dir=json_data.get("handout_dir", None),
        )

        dockerfile_locations = json_data.get("dockerfile_locations", [])
        for location in dockerfile_locations:
            challenge.add_dockerfile_location(
                [
                    DockerfileLocation(
                        location.get("location", "src/Dockerfile"),
                        location.get("context", "src/"),
                        location.get("identifier", None),
                    )
                ]
            )

        prerequisites = json_data.get("prerequisites", [])
        for prerequisite in prerequisites:
            challenge.add_prerequisite(prerequisite)

        return challenge

    @staticmethod
    def load(file):
        if file.endswith((".yml", ".yaml")):
            print("Loading from yml file")
            return Challenge.load_from_yaml(Utils.load_yaml(file))
        elif file.endswith(".json"):
            print("Loading from json file")
            return Challenge.load_from_json(Utils.load_json(file))
        else:
            print("File must be either a yml or json file.")
            raise ValueError("File must be either a yml or json file.")

    @staticmethod
    def load_dir(directory: Path):
        # Check for yml or json file
        path = Path(directory)
        for file in path.iterdir():
            if not file.is_file():
                continue

            if file.name.endswith(".yml") or file.name.endswith(".yaml"):
                print("Loading from yml file")
                return Challenge.load_from_yaml(Utils.load_yaml(file))
            elif file.name.endswith(".json"):
                print("Loading from json file")
                return Challenge.load_from_json(Utils.load_json(file))


@dataclass
class Page:
    enabled: bool = True
    slug: str = ""
    title: str = ""
    route: str = ""
    content: str = "page.md"
    format: str = "markdown"
    auth: bool = False
    draft: bool = False

    def __post_init__(self):
        self.validate_slug()
        self.validate_title()
        self.validate_route()
        self.validate_content()
        self.validate_format()

    def validate_slug(self):
        if not Utils.validate_length(self.slug, 1, 50, "slug"):
            raise ValueError("Slug must be between 1 and 50 characters.")

    def validate_title(self):
        if not Utils.validate_length(self.title, 1, 100, "title"):
            raise ValueError("Title must be between 1 and 100 characters.")

    def validate_route(self):
        if not Utils.validate_length(self.route, 1, 100, "route"):
            raise ValueError("Route must be between 1 and 100 characters.")

    def validate_content(self):
        if not re.match(r"^[a-zA-Z0-9-_.]+\.(md|html|txt)$", self.content):
            raise ValueError(
                "Content must be a valid file path ending in .md, .html, or .txt."
            )

    def validate_format(self):
        if self.format not in ("markdown", "html"):
            raise ValueError("Format must be either 'markdown' or 'html'.")

    def get_version(self):
        file = self.get_path().joinpath("version")

        if not file.exists():
            return 0

        with open(file, "r") as f:
            return int(f.read())

    def save_version(self, version: int):
        file = self.get_path().joinpath("version")

        with open(file, "w") as f:
            f.write(str(version))

    def get_path(self):
        return Utils.get_page_dir(self.slug)

    def generate_dict(self, schema_location: str):
        return {
            "$schema": schema_location,
            "enabled": self.enabled,
            "slug": self.slug,
            "title": self.title,
            "route": self.route,
            "content": self.content,
            "format": self.format,
            "auth": self.auth,
            "draft": self.draft,
        }

    def str_yml(self, schema_location: str):
        data = self.generate_dict(schema_location)
        schema = data.pop("$schema", None)
        yml_str = f"# yaml-language-server: $schema={schema}\n\n"
        yml_str += _yaml.dump(data, sort_keys=False, allow_unicode=True)
        return yml_str

    def str_json(self, schema_location: str):
        data = self.generate_dict(schema_location)
        return _json.dumps(data, indent=2)

    def __str__(self):
        return self.str_yml("-")

    @staticmethod
    def load_from_yaml(yml: dict):
        if yml is None:
            raise ValueError("YAML data must not be None.")
        return Page(
            enabled=yml.get("enabled", True),
            slug=yml.get("slug", ""),
            title=yml.get("title", ""),
            route=yml.get("route", ""),
            content=yml.get("content", "page.md"),
            format=yml.get("format", "markdown"),
            auth=yml.get("auth", False),
            draft=yml.get("draft", False),
        )

    @staticmethod
    def load_from_json(json_data: dict):
        if json_data is None:
            raise ValueError("JSON data must not be None.")
        return Page(
            enabled=json_data.get("enabled", True),
            slug=json_data.get("slug", ""),
            title=json_data.get("title", ""),
            route=json_data.get("route", ""),
            content=json_data.get("content", "page.md"),
            format=json_data.get("format", "markdown"),
            auth=json_data.get("auth", False),
            draft=json_data.get("draft", False),
        )

    @staticmethod
    def load(file):
        if file.endswith((".yml", ".yaml")):
            return Page.load_from_yaml(Utils.load_yaml(file))
        elif file.endswith(".json"):
            return Page.load_from_json(Utils.load_json(file))
        else:
            raise ValueError("File must be either a yml or json file.")

    @staticmethod
    def load_dir(directory: Path):
        # Check for yml or json file
        path = Path(directory)
        for file in path.iterdir():
            if file.is_file():
                if file.name.endswith(".yml") or file.name.endswith(".yaml"):
                    print("Loading from yml file")
                    return Page.load_from_yaml(Utils.load_yaml(file))
                elif file.name.endswith(".json"):
                    print("Loading from json file")
                    return Page.load_from_json(Utils.load_json(file))
