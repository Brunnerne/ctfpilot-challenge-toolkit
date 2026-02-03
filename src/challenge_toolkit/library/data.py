import re
import json as _json
import yaml as _yaml

from dataclasses import dataclass, field
from typing import List, Optional, Union
from pathlib import Path


from .utils import Utils
from .config import CHALL_TYPES, DIFFICULTIES, CATEGORIES, TAG_FORMAT, INSTANCED_TYPES, FLAG_FORMAT, DEFAULT

@dataclass
class DockerfileLocation:
    location: str
    context: str
    identifier: Optional[str] = None
    
    def __init__(self, location, context, identifier):
        self.set_location(location)
        self.set_context(context)
        self.set_identifier(identifier)
    
    def set_location(self, location: str):
        if not re.match(r'^[a-zA-Z0-9-_/\.]+$', location):
            print("Dockerfile location must be a valid file path to a Dockerfile.")
            raise ValueError("Dockerfile location must be a valid file path to a Dockerfile.")
        
        self.location = location
        
    def set_context(self, context: str):
        if not re.match(r'^[a-zA-Z0-9-_/\.]+$', context):
            print("Dockerfile context must be a valid file path.")
            raise ValueError("Dockerfile context must be a valid file path.")
        
        self.context = context
        
    def set_identifier(self, identifier: Optional[str]):
        identifier = Utils.slugify(identifier) or None
        
        if identifier is None:
            self.identifier = None
            return
        
        if identifier != None and Utils.validate_length(identifier, 1, 50, "identifier") == False:
            raise ValueError("Identifier must be between 1 and 50 characters.")
        
        self.identifier = identifier

@dataclass
class ChallengeFlag:
    flag: str
    case_sensitive: bool = False
    
    def __init__(self, flag: str, case_sensitive: bool = False):
        if not Utils.validate_length(flag, 1, 1000, "flag"):
            raise ValueError("Flag must be between 1 and 1000 characters.")
        
        flag = flag.strip().replace('\n', '').replace('\r', '')
        if not re.match(FLAG_FORMAT, flag):
            print("Flag must be in the format: " + FLAG_FORMAT)
            raise ValueError("The flag \""+flag+"\" must be in the format: " + FLAG_FORMAT)
        
        self.flag = flag
        self.case_sensitive = case_sensitive
        
    def to_dict(self):
        return {
            "flag": self.flag,
            "case_sensitive": self.case_sensitive
        }

@dataclass
class Challenge:
    name: str
    slug: str
    author: str
    category: str
    difficulty: str
    type: str
    tags: Optional[List[str]] = field(default_factory=list)
    instanced_type: str = "none"
    instanced_name: Optional[str] = None
    instanced_subdomains: List[str] = field(default_factory=list)
    connection: Optional[str] = None
    flag: Optional[List[ChallengeFlag]] = None
    enabled: bool = True
    points: int = 1000
    decay: int = 75
    min_points: int = 100
    description_location: str = "description.md"
    handout_dir: str = "handout"
    dockerfile_locations: List[DockerfileLocation] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    
    def __init__(
        self, 
        enabled: bool = True,
        name: Optional[str] = None, 
        slug: Optional[str] = None, 
        author: Optional[str] = None, 
        category: Optional[str] = None, 
        difficulty: Optional[str] = None, 
        type: Optional[str] = None,
        instanced_type: Optional[str] = None, 
        instanced_name: Optional[str] = None,
        instanced_subdomains: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        connection: Optional[str] = None,
        flag: Optional[Union[str, List[str], List[dict], ChallengeFlag, List[ChallengeFlag]]] = None,
        points: Optional[int] = None, 
        decay: Optional[int] = None,
        min_points: Optional[int] = None,
        description_location: Optional[str] = None,
        handout_dir: Optional[str] = None
    ):
        # Insert default values from DEFAULT
        if enabled is not None:
            self.set_enabled(enabled)
        else: self.set_enabled(DEFAULT['enabled'])
        if name is not None:
            self.set_name(name)
        else: self.set_name(DEFAULT['name'])
        if slug is not None:
            self.set_slug(slug)
        else: self.set_slug(DEFAULT['slug'])
        if author is not None:
            self.set_author(author)
        else: self.set_author(DEFAULT['author'])
        if category is not None:
            self.set_category(category)
        else: self.set_category(DEFAULT['category'])
        if difficulty is not None:
            self.set_difficulty(difficulty)
        else: self.set_difficulty(DEFAULT['difficulty'])
        if type is not None:
            self.set_type(type)
        else: self.set_type(DEFAULT['type'])
        if instanced_type is not None:
            self.set_instanced_type(instanced_type)
        else: self.set_instanced_type(DEFAULT['instanced_type'])
        if tags is not None:
            self.set_tags(tags)
        else: self.set_tags(DEFAULT['tags'])
        if instanced_name is not None:
            self.instanced_name = instanced_name
        else: self.instanced_name = DEFAULT['instanced_name']
        if instanced_subdomains is not None:
            self.set_instanced_subdomains(instanced_subdomains)
        else: self.instanced_subdomains = DEFAULT['instanced_subdomains']
        if connection is not None:
            self.set_connection(connection)
        else: self.connection = DEFAULT['connection']
        if flag is not None:
            self.set_flag(flag)
        else: self.set_flag(DEFAULT['flag'])
        if points is not None:
            self.set_points(points)
        else: self.set_points(DEFAULT['points'])
        if decay is not None:
            self.set_decay(decay)
        else: self.set_decay(DEFAULT['decay'])
        if min_points is not None:
            self.set_min_points(min_points)
        else: self.set_min_points(DEFAULT['min_points'])
        if description_location is not None:
            self.set_description_location(description_location)
        else: self.set_description_location(DEFAULT['description_location'])
        if handout_dir is not None:
            self.set_handout_dir(handout_dir)
        else: self.set_handout_dir(DEFAULT['handout_dir'])

        self.prerequisites = []
        self.dockerfile_locations = []
        
    
    def set_enabled(self, enabled: bool):
        if not isinstance(enabled, bool):
            raise ValueError("Enabled must be a boolean")
        
        self.enabled = enabled
    
    def set_name(self, name: str):
        if Utils.validate_length(name, 1, 50, "name") == False:
            raise ValueError("Name must be between 1 and 50 characters.")
        
        self.name = name
        
    def set_slug(self, slug: str):
        slug = Utils.slugify(slug) or ""
        
        if Utils.validate_length(slug, 1, 50, "slug") == False:
            raise ValueError("Slug must be between 1 and 50 characters.")
        
        self.slug = slug
        
    def set_author(self, author: str):
        if Utils.validate_length(author, 1, 100, "author") == False:
            raise ValueError("Author must be between 1 and 100 characters.")
        
        self.author = author
        
    def set_category(self, category: str):
        if Utils.validate_length(category, 1, 50, "category") == False:
            raise ValueError("Category must be between 1 and 50 characters.")
        
        if category not in CATEGORIES:
            print("Category must be one of the following: " + ", ".join(CATEGORIES))
            raise ValueError("Invalid category provided. Category must be one of the following: " + ", ".join(CATEGORIES))
        
        self.category = category
        
    def set_difficulty(self, difficulty: str):
        if difficulty is None:
            print("Difficulty must be provided.")
            raise ValueError("Difficulty must be provided.")
        
        difficulty = difficulty.lower()
        if difficulty not in DIFFICULTIES:
            print("Difficulty must be one of the following: " + ", ".join(DIFFICULTIES))
            raise ValueError("Invalid difficulty provided. Difficulty must be one of the following: " + ", ".join(DIFFICULTIES))
        
        self.difficulty = difficulty
        
    def set_type(self, type: str):
        if type is None:
            print("Type must be provided.")
            raise ValueError("Type must be provided.")
        
        type = type.lower()
        if type not in CHALL_TYPES:
            print("Type must be one of the following: " + ", ".join(CHALL_TYPES))
            raise ValueError("Invalid type provided. Type must be one of the following: " + ", ".join(CHALL_TYPES))
        self.type = type
        
    def set_tags(self, tags: List[str]):
        if not isinstance(tags, list):
            print("Tags must be a list of strings.")
            raise ValueError("Tags must be a list of strings.")
        
        for tag in tags:
            if not re.match(TAG_FORMAT, tag):
                print(f"Tag '{tag}' does not match the required format: {TAG_FORMAT}")
                raise ValueError(f"Tag '{tag}' does not match the required format: {TAG_FORMAT}")
        
        self.tags = tags
        
    def set_points(self, points: int):
        if points < 1 or points > 10000:
            print("Points must be between 1 and 10000.")
            raise ValueError("Points must be between 1 and 10000.")
        
        self.points = points
        
    def set_decay(self, decay: int):
        if decay < 0 or decay > 10000:
            print("Decay must be between 0 and 10000.")
            raise ValueError("Decay must be between 0 and 10000.")
        
        self.decay = decay
        
    def set_min_points(self, min_points: int):
        if min_points < 1 or min_points > 1000:
            print("Minimum points must be between 1 and 1000.")
            raise ValueError("Minimum points must be between 1 and 1000.")
        
        self.min_points = min_points
        
    def set_instanced_subdomains(self, instanced_subdomains: List[str]):
        if not isinstance(instanced_subdomains, list):
            print("Instanced subdomains must be a list of strings.")
            raise ValueError("Instanced subdomains must be a list of strings.")
        
        if len(instanced_subdomains) > 5:
            print("Instanced subdomains must not exceed 5 items.")
            raise ValueError("Instanced subdomains must not exceed 5 items.")
        
        for subdomain in instanced_subdomains:
            if not re.match(r'^((web|tcp):)?[a-z0-9-]+$', subdomain):
                print(f"Subdomain '{subdomain}' does not match the required format: ^((web|tcp):)?[a-z0-9-]+$")
                raise ValueError(f"Subdomain '{subdomain}' does not match the required format: ^((web|tcp):)?[a-z0-9-]+$")

            if len(subdomain) > 10:
                print(f"Subdomain '{subdomain}' exceeds the maximum length of 10 characters.")
                raise ValueError(f"Subdomain '{subdomain}' exceeds the maximum length of 10 characters.")
        
        self.instanced_subdomains = instanced_subdomains
        
    def set_connection(self, connection: Optional[str]):
        if connection is not None and not isinstance(connection, str):
            print("Connection must be a string or None.")
            raise ValueError("Connection must be a string or None.")
        
        # Max length of 255
        if Utils.validate_length(connection, 1, 255, "connection") == False:
            raise ValueError("Connection string must be between 1 and 255 characters.")

        self.connection = connection
    
    def set_flag(self, flag):
        if isinstance(flag, list):
            clean_flags = []
            for f in flag:
                if isinstance(f, ChallengeFlag):
                    clean_flags.append(f)
                elif isinstance(f, str):
                    clean_flags.append(ChallengeFlag(f))
                elif isinstance(f, dict):
                    if 'flag' not in f or not isinstance(f['flag'], str):
                        raise ValueError("Each flag dictionary must contain a 'flag' key with a string value.")
                    case_sensitive = f.get('case_sensitive', False)
                    clean_flags.append(ChallengeFlag(f['flag'], case_sensitive))
            if not clean_flags:
                raise ValueError("No valid flags provided in list.")
            self.flag = clean_flags
        elif isinstance(flag, str):
            self.flag = [ChallengeFlag(flag)]
        elif isinstance(flag, ChallengeFlag):
            self.flag = [flag]
        else:
            self.flag = None
        
    def set_instanced_type(self, instanced_type: str):
        instanced_type = instanced_type.lower()
        if instanced_type not in INSTANCED_TYPES:
            print("Instanced type must be one of the following: " + ", ".join(INSTANCED_TYPES))
            raise ValueError("Invalid instanced type provided. Instanced type must be one of the following: " + ", ".join(INSTANCED_TYPES))
        
        self.instanced_type = instanced_type
        
    def set_instanced_name(self, instanced_name: Optional[str]):
        instanced_name = Utils.slugify(instanced_name)
        
        if Utils.validate_length(instanced_name, 1, 50, "instanced_name") == False:
            raise ValueError("Instanced name must be between 1 and 50 characters.")
        
        self.instanced_name = instanced_name
        
    def set_description_location(self, description_location: str):
        if not re.match(r'^[a-zA-Z0-9-_/]+.md$', description_location):
            print("Description location must be a valid file path to a Markdown file.")
            raise ValueError("Description location must be a valid file path to a Markdown file.")
        
        self.description_location = description_location
    
    def get_description(self):
        file = self.get_path().joinpath(self.description_location)
        
        if not file.exists():
            return ""
        
        with open(file, 'r') as f:
            return f.read()
        
    def set_handout_dir(self, handout_dir: str):
        if not re.match(r'^[a-zA-Z0-9-_/]+$', handout_dir):
            print("Handout directory must be a valid file path.")
            raise ValueError("Handout directory must be a valid file path.")
        
        self.handout_dir = handout_dir
    
    def add_dockerfile_location(self, locations: List[DockerfileLocation]):
        self.dockerfile_locations.extend(locations)
        
    def add_prerequisite(self, prerequisite: Optional[str]):
        prerequisite = Utils.slugify(prerequisite)
        
        if prerequisite is None:
            print("Prerequisite must be provided.")
            raise ValueError("Prerequisite must be provided.")
        
        if Utils.validate_length(prerequisite, 1, 50, "prerequisite") == False:
            raise ValueError("Prerequisite must be between 1 and 50 characters.")
        
        if prerequisite in self.prerequisites:
            print(f"Prerequisite {prerequisite} already exists.")
            raise ValueError("Prerequisite already exists.")
        
        self.prerequisites.append(prerequisite)
        
    def get_version(self):
        file = self.get_path().joinpath('version')
        
        if not file.exists():
            return 0
        
        with open(file, 'r') as f:
            return int(f.read())

    def save_version(self, version: int):
        file = self.get_path().joinpath('version')
        
        with open(file, 'w') as f:
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
            "points": self.points,
            "decay": self.decay,
            "min_points": self.min_points,
            "description_location": self.description_location,
            "handout_dir": self.handout_dir
        }
        if self.dockerfile_locations:
            data["dockerfile_locations"] = [
                {
                    "location": loc.location,
                    "context": loc.context,
                    "identifier": loc.identifier
                } for loc in self.dockerfile_locations
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
            points=yml.get("points", 1000),
            decay=yml.get("decay", 75),
            min_points=yml.get("min_points", 100),
            description_location=yml.get("description_location", "description.md"),
            handout_dir=yml.get("handout_dir", "handout")
        )

        dockerfile_locations = yml.get("dockerfile_locations", [])
        for location in dockerfile_locations:
            challenge.add_dockerfile_location([DockerfileLocation(location.get("location", "src/Dockerfile"), location.get("context", "src/"), location.get("identifier", None))])

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
            points=json_data.get("points", 1000),
            decay=json_data.get("decay", 75),
            min_points=json_data.get("min_points", 100),
            description_location=json_data.get("description_location", "description.md"),
            handout_dir=json_data.get("handout_dir", "handout")
        )

        dockerfile_locations = json_data.get("dockerfile_locations", [])
        for location in dockerfile_locations:
            challenge.add_dockerfile_location([DockerfileLocation(location.get("location", "src/Dockerfile"), location.get("context", "src/"), location.get("identifier", None))])

        prerequisites = json_data.get("prerequisites", [])
        for prerequisite in prerequisites:
            challenge.add_prerequisite(prerequisite)

        return challenge
    
    @staticmethod
    def load(file):
        if file.endswith(".yml") or file.endswith(".yaml"):
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
            if file.is_file():
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
    auth: Optional[bool] = False
    draft: Optional[bool] = False

    def __init__(
        self,
        enabled: bool = True,
        slug: Optional[str] = None,
        title: Optional[str] = None,
        route: Optional[str] = None,
        content: Optional[str] = None,
        format: Optional[str] = None,
        auth: Optional[bool] = None,
        draft: Optional[bool] = None,
    ):
        if enabled != None:
            self.set_enabled(enabled)
        if slug != None:
            self.set_slug(slug)
        if title != None:
            self.set_title(title)
        if route != None:
            self.set_route(route)
        if content != None:
            self.set_content(content)
        if format != None:
            self.set_format(format)
        if auth != None:
            self.set_auth(auth)
        if draft != None:
            self.set_draft(draft)

    def set_enabled(self, enabled: bool):
        self.enabled = enabled

    def set_slug(self, slug: str):
        if not Utils.validate_length(slug, 1, 50, "slug"):
            raise ValueError("Slug must be between 1 and 50 characters.")
        self.slug = slug

    def set_title(self, title: str):
        if not Utils.validate_length(title, 1, 100, "title"):
            raise ValueError("Title must be between 1 and 100 characters.")
        self.title = title

    def set_route(self, route: str):
        if not Utils.validate_length(route, 1, 100, "route"):
            raise ValueError("Route must be between 1 and 100 characters.")
        self.route = route

    def set_content(self, content: str):
        if not re.match(r'^[a-zA-Z0-9-_.]+\.(md|html|txt)$', content):
            raise ValueError("Content must be a valid file path ending in .md, .html, or .txt.")
        self.content = content

    def set_format(self, format: str):
        if format not in ["markdown", "html"]:
            raise ValueError("Format must be either 'markdown' or 'html'.")
        self.format = format

    def set_auth(self, auth: Optional[bool]):
        self.auth = auth if auth is not None else False

    def set_draft(self, draft: Optional[bool]):
        self.draft = draft if draft is not None else False
        
    def get_version(self):
        file = self.get_path().joinpath('version')
        
        if not file.exists():
            return 0
        
        with open(file, 'r') as f:
            return int(f.read())

    def save_version(self, version: int):
        file = self.get_path().joinpath('version')
        
        with open(file, 'w') as f:
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
        if file.endswith(".yml") or file.endswith(".yaml"):
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
                