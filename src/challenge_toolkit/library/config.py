from pathlib import Path

# Path to the root of the challenge repository
CHALLENGE_REPO_ROOT = Path.cwd() # Default to the directory where the command is run from

# Challenge and Page schema URLs
CHALLENGE_SCHEMA = "https://raw.githubusercontent.com/ctfpilot/challenge-schema/refs/heads/main/schema.json"
PAGE_SCHEMA = "https://raw.githubusercontent.com/ctfpilot/page-schema/refs/heads/main/schema.json"

# Allowed values for schema fields
CHALL_TYPES = [ "static", "shared", "instanced" ]
DIFFICULTIES = [ "beginner", "easy", "easy-medium", "medium", "medium-hard", "hard", "very-hard", "insane"]
CATEGORIES = [ "web", "forensics", "rev", "crypto", "pwn", "boot2root", "osint", "misc", "blockchain", "mobile", "test" ]
INSTANCED_TYPES = [ "none", "web", "tcp" ] # "none" is the default. Defines how users interact with the challenge.

# Regex patterns for tag and flag validation
TAG_FORMAT = "^[a-zA-Z0-9-_:;? ]+$"
FLAG_FORMAT = "^(\\w{2,10}\\{[^}]*\\}|dynamic|null)$"

# Default challenge configuration values
DEFAULT = {
    "enabled": False,
    "name": None,
    "slug": None,
    "author": None,
    "category": None,
    "difficulty": None,
    "type": None,
    "tags": [],
    "instanced_name": None,
    "instanced_type": "none",
    "instanced_subdomains": [],
    "connection": None,
    "flag": {"flag": "null", "case_sensitive": False},
    "points": 1000,
    "decay": 75,
    "min_points": 100,
    "description_location": "description.md",
    "handout_dir": "handout"
}
