"""
Template Generator for CTF Challenges

Prompts the user for inputs and generates a template for a CTF challenge.
"""

import argparse
import sys

from challenge_toolkit.library.config import (
    CATEGORIES,
    CHALL_TYPES,
    DIFFICULTIES,
    FLAG_FORMAT,
    INSTANCED_TYPES,
)
from challenge_toolkit.library.data import Challenge, DockerfileLocation
from challenge_toolkit.library.generator import Generator as OSGenerator
from challenge_toolkit.library.utils import Utils


class Args:
    args = None
    subcommand = False

    def __init__(self, parent_parser=None):
        if parent_parser:
            self.subcommand = True
            self.parser = parent_parser.add_parser(
                "create", help="Template Generator for CTF Challenges"
            )
        else:
            self.parser = argparse.ArgumentParser(
                description="Template Generator for CTF Challenges"
            )

        self.parser.add_argument(
            "--no-prompts",
            help="Skip prompts and use default values",
            action="store_true",
        )
        self.parser.add_argument("--name", help="Name of the challenge")
        self.parser.add_argument("--slug", help="Slug of the challenge")
        self.parser.add_argument("--author", help="Author of the challenge")
        self.parser.add_argument("--category", help="Category of the challenge")
        self.parser.add_argument("--difficulty", help="Difficulty of the challenge")
        self.parser.add_argument("--type", help="Type of the challenge")
        self.parser.add_argument(
            "--instanced-type", help="Type of instanced challenge", default="none"
        )
        self.parser.add_argument("--flag", help="Flag for the challenge", type=str)
        self.parser.add_argument(
            "--points", help="Points for the challenge", type=int, default=1000
        )
        self.parser.add_argument(
            "--min-points",
            help="Minimum points for the challenge",
            type=int,
            default=100,
        )
        self.parser.add_argument(
            "--description-location",
            help="Location of the description file",
            default="description.md",
        )
        self.parser.add_argument(
            "--dockerfile-location",
            help="Location of the Dockerfile",
            default="src/Dockerfile",
        )
        self.parser.add_argument(
            "--dockerfile-context", help="Context of the Dockerfile", default="src/"
        )
        self.parser.add_argument(
            "--dockerfile-identifier", help="Identifier of the Dockerfile", default=None
        )
        self.parser.add_argument(
            "--handout-location", help="Location of the handout", default="handout"
        )

    def parse(self):
        if self.subcommand:
            self.args = self.parser.parse_args(sys.argv[2:])
        else:
            self.args = self.parser.parse_args()

    def prompt_arg(self, arg, text, validator, default=None):
        # If set as arg, return this unless it's just the default
        if arg is not None and (default is None or arg == default):
            return arg

        default_text = f" ({default})" if default else ""
        while True:
            try:
                result = input(f"{text}{default_text}: ")
                if default is not None and result == "":
                    result = default
                validator(result)
                return result
            except (ValueError, TypeError) as e:
                print(e)

    def prompt(self) -> Challenge:
        args = self.args

        if args is None:
            # Convert to object if args is None
            args = self.args = self.parser.parse_args()

        name = self.prompt_arg(args.name, "Challenge name", Challenge.validate_name)
        slug = self.prompt_arg(
            args.slug,
            "Challenge slug",
            Challenge.validate_slug,
            default=Utils.slugify(name) or "challenge",
        )
        author = self.prompt_arg(
            args.author, "Challenge author", Challenge.validate_author
        )
        category = self.prompt_arg(
            args.category,
            f"Challenge category ({', '.join(CATEGORIES)})",
            Challenge.validate_category,
        ).lower()
        difficulty = self.prompt_arg(
            args.difficulty,
            f"Challenge difficulty ({', '.join(DIFFICULTIES)})",
            Challenge.validate_difficulty,
        )
        chall_type = self.prompt_arg(
            args.type,
            "Challenge type",
            Challenge.validate_type,
            default=", ".join(CHALL_TYPES),
        )
        flag = self.prompt_arg(
            args.flag, "Challenge flag", Challenge.validate_flag, FLAG_FORMAT
        )
        points = int(
            self.prompt_arg(args.points, "Challenge points", Challenge.validate_points, 1000),
        )
        min_points = int(
            self.prompt_arg(
                args.min_points,
                "Challenge minimum points",
                Challenge.validate_min_points,
                100,
            )
        )
        decay = int(
            self.prompt_arg(args.decay, "Challenge point decay", Challenge.validate_decay, 75),
        )

        if chall_type in ("instanced", "shared"):
            instanced_type = self.prompt_arg(
                args.instanced_type,
                f"Instanced type ({', '.join(INSTANCED_TYPES)})",
                Challenge.validate_instanced_type,
            ).lower()
        else:
            instanced_type = "none"
        
        description_location = self.prompt_arg(
            args.description_location,
            "Location of the description file",
            Challenge.validate_description_location,
            default="description.md"
        )
        
        handout_location = self.prompt_arg(
            args.handout_location,
            "Location of handout folder",
            Challenge.validate_handout_dir,
            default="handout"
        )
        
        challenge = Challenge(
            name=name,
            slug=slug,
            author=author,
            category=category,
            difficulty=difficulty,
            type=chall_type,
            instanced_type=instanced_type,
            flag=flag,
            points=points,
            decay=decay,
            min_points=min_points,
            description_location=description_location,
            handout_dir=handout_location
        )

        """
        if (
            args.dockerfile_location is None
            or args.dockerfile_location == "src/Dockerfile"
        ):
            contains_docker = (
                input("Does the challenge contain a Dockerfile? (y/N): ").lower() == "y"
            )
            if contains_docker:
                while True:
                    try:
                        dockerfile_location = (
                            input("Location of the Dockerfile (src/Dockerfile): ")
                            or "src/Dockerfile"
                        )
                        dockerfile_context = (
                            input("Context of the Dockerfile (src/): ") or "src/"
                        )
                        dockerfile_identifier = (
                            input("Identifier of the Dockerfile: ") or None
                        )

                        challenge.add_dockerfile_location(
                            [
                                DockerfileLocation(
                                    dockerfile_location,
                                    dockerfile_context,
                                    dockerfile_identifier,
                                )
                            ]
                        )
                        break
                    except ValueError:
                        print("Invalid Dockerfile location. Please try again.")
        """
        return challenge


class Generator:
    def __init__(self, challenge: Challenge):
        self.challenge = challenge
        self.path = Utils.get_challenge_dir(challenge.category, challenge.slug)
        self.generator = OSGenerator(challenge)

    def generate(self):
        self.generator.build()


class ChallengeCreator:
    args = None
    parent_parser = None

    def __init__(self, parent_parser=None):
        self.parent_parser = parent_parser

    def register_subcommand(self):
        self.args = Args(self.parent_parser)

    def run(self):
        if not self.args:
            arguments = Args(self.parent_parser)
            arguments.parse()
            self.args = arguments
        else:
            self.args.parse()

        arguments = self.args
        args = self.args.args

        if not args:
            print(
                "Error parsing arguments. Please run with --help to see available options."
            )
            sys.exit(1)

        if args.name and args.slug is None:
            args.slug = Utils.slugify(args.name) if args.name else "challenge"

        if not args.no_prompts:
            challenge = arguments.prompt()

            print("\nInformation filled out.")

            print("\nInformation for the challenge:")
            print(challenge)

            print("\nIs the information correct?")
            if (input("Y/n: ") or "y").lower() != "y":
                print("Exiting...")
                sys.exit(1)

        else:
            challenge = Challenge(
                name=args.name,
                slug=args.slug,
                author=args.author,
                category=args.category,
                difficulty=args.difficulty,
                type=args.type,
                instanced_type=args.instanced_type or "none",
                flag=args.flag,
                points=args.points or 1000,
                min_points=args.min_points or 100,
                description_location=args.description_location,
                handout_dir=args.handout_location,
            )

            if args.type != "static":
                try:
                    if args.dockerfile_location:
                        challenge.add_dockerfile_location(
                            [
                                DockerfileLocation(
                                    args.dockerfile_location,
                                    args.dockerfile_context,
                                    args.dockerfile_identifier,
                                )
                            ]
                        )
                except ValueError:
                    sys.exit(1)

        generator = Generator(challenge)
        generator.generate()


if __name__ == "__main__":
    ChallengeCreator().run()
