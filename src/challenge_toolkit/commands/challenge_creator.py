'''
Template Generator for CTF Challenges

Prompts the user for inputs and generates a template for a CTF challenge.
'''

import sys
import argparse

from challenge_toolkit.library.config import CHALL_TYPES, DIFFICULTIES, FLAG_FORMAT, INSTANCED_TYPES, CATEGORIES
from challenge_toolkit.library.utils import Utils
from challenge_toolkit.library.data import Challenge, DockerfileLocation
from challenge_toolkit.library.generator import Generator as OSGenerator

class Args:
    args = None
    subcommand = False

    def __init__(self, parent_parser = None):
        if parent_parser:
            self.subcommand = True
            self.parser = parent_parser.add_parser("create", help="Template Generator for CTF Challenges")
        else:
            self.parser = argparse.ArgumentParser(description="Template Generator for CTF Challenges")

        self.parser.add_argument("--no-prompts", help="Skip prompts and use default values", action="store_true")
        self.parser.add_argument("--name", help="Name of the challenge")
        self.parser.add_argument("--slug", help="Slug of the challenge")
        self.parser.add_argument("--author", help="Author of the challenge")
        self.parser.add_argument("--category", help="Category of the challenge")
        self.parser.add_argument("--difficulty", help="Difficulty of the challenge")
        self.parser.add_argument("--type", help="Type of the challenge")
        self.parser.add_argument("--instanced-type", help="Type of instanced challenge", default="none")
        self.parser.add_argument("--flag", help="Flag for the challenge", type=str)
        self.parser.add_argument("--points", help="Points for the challenge", type=int, default=1000)
        self.parser.add_argument("--min-points", help="Minimum points for the challenge", type=int, default=100)
        self.parser.add_argument("--description-location", help="Location of the description file", default="description.md")
        self.parser.add_argument("--dockerfile-location", help="Location of the Dockerfile", default="src/Dockerfile")
        self.parser.add_argument("--dockerfile-context", help="Context of the Dockerfile", default="src/")
        self.parser.add_argument("--dockerfile-identifier", help="Identifier of the Dockerfile", default=None)
        self.parser.add_argument("--handout_location", help="Location of the handout", default="handout")

    def parse(self):
        if self.subcommand:
            self.args = self.parser.parse_args(sys.argv[2:])
        else:
            self.args = self.parser.parse_args()

    def prompt(self, challenge: Challenge):
        args = self.args

        if args is None:
            # Convert to object if args is None
            args = self.args = self.parser.parse_args()

        # Ensure args is not None before accessing its attributes
        if args.name is None:
            while True:
                try:
                    challenge.set_name(input("Name of the challenge: "))
                    break
                except ValueError:
                    print("Invalid name. Please try again.")
        else:
            challenge.set_name(args.name)

        if args.slug is None:
            while True:
                try:
                    challenge.set_slug(input(f"Slug of the challenge ({Utils.slugify(challenge.name)}): ") or Utils.slugify(challenge.name) or "challenge")
                    break
                except ValueError:
                    print("Invalid slug. Please try again.")
        else:
            challenge.set_slug(args.slug)

        if args.author is None:
            while True:
                try:
                    challenge.set_author(input("Author of the challenge: "))
                    break
                except ValueError:
                    print("Invalid author. Please try again.")
        else:
            challenge.set_author(args.author)

        if args.category is None:
            while True:
                try:
                    challenge.set_category(input(f"Category of the challenge ({', '.join(CATEGORIES)}): ").lower())
                    break
                except ValueError:
                    print("Invalid category. Please try again.")
        else:
            challenge.set_category(args.category)

        if args.difficulty is None:
            while True:
                try:
                    challenge.set_difficulty(input(f"Difficulty of the challenge ({', '.join(DIFFICULTIES)}): ").lower())
                    break
                except ValueError:
                    print("Invalid difficulty. Please try again.")
        else:
            challenge.set_difficulty(args.difficulty)

        prompted_type = None
        if args.type is None:
            while True:
                try:
                    prompted_type = input(f"Type of the challenge ({', '.join(CHALL_TYPES)}): ").lower()
                    challenge.set_type(prompted_type)
                    break
                except ValueError:
                    print("Invalid type. Please try again.")
        else:
            challenge.set_type(args.type)
            prompted_type = args.type

        if args.flag is None:
            while True:
                try:
                    challenge.set_flag(input(f"Flag for the challenge ({FLAG_FORMAT}): "))
                    break
                except ValueError:
                    print("Invalid flag. Please try again.")
        else:
            challenge.set_flag(args.flag)

        if args.points is None:
            while True:
                try:
                    challenge.set_points(int(input("Points for the challenge (1000): ") or 1000))
                    break
                except ValueError:
                    print("Invalid points. Please try again.")
        else:
            challenge.set_points(args.points)

        if args.min_points is None:
            while True:
                try:
                    challenge.set_min_points(int(input("Minimum points for the challenge (100): ") or 100 ))
                    break
                except ValueError:
                    print("Invalid minimum points. Please try again.")
        else:
            challenge.set_min_points(args.min_points)

        if (args.type in [ "instanced", "shared" ] or prompted_type in [ "instanced", "shared" ]) and args.instanced_type == "none":
            while True:
                try:
                    challenge.set_instanced_type(input(f"Instanced type for challenge ({', '.join(INSTANCED_TYPES)}): ").lower())
                    break
                except ValueError:
                    print("Invalid instanced type. Please try again.")
        elif args.instanced_type != "none":
            challenge.set_instanced_type(args.instanced_type)
        else:
            challenge.set_instanced_type("none")

        if args.description_location == "description.md":
            while True:
                try:
                    challenge.set_description_location(input("Location of the description file (description.md): ") or "description.md")
                    break
                except ValueError:
                    print("Invalid description location. Please try again.")
        else:
            challenge.set_description_location(args.description_location)

        if args.dockerfile_location is None or args.dockerfile_location == "src/Dockerfile":
            contains_docker = input("Does the challenge contain a Dockerfile? (y/N): ").lower() == "y"
            if contains_docker:
                while True:
                    try:
                        dockerfile_location = input("Location of the Dockerfile (src/Dockerfile): ") or "src/Dockerfile"
                        dockerfile_context = input("Context of the Dockerfile (src/): ") or "src/"
                        dockerfile_identifier = input("Identifier of the Dockerfile: ") or None

                        challenge.add_dockerfile_location([ DockerfileLocation(dockerfile_location, dockerfile_context, dockerfile_identifier) ])
                        break
                    except ValueError:
                        print("Invalid Dockerfile location. Please try again.")

        if args.handout_location == "handout":
            contains_handout = input("What is the location of the handout for handing out with the challenge? (handout): ") or "handout"
            if contains_handout:
                challenge.set_handout_dir(contains_handout)
        else:
            challenge.set_handout_dir(args.handout_location)

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

    def __init__(self, parent_parser = None):
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
            print("Error parsing arguments. Please run with --help to see available options.")
            sys.exit(1)

        if args.name and args.slug is None:
            args.slug = Utils.slugify(args.name) if args.name else "challenge"

        challenge = None
        if args.no_prompts == False:
            challenge = Challenge(name="demo", slug="demo", author="demo", category="misc", difficulty="easy", type="static", flag="flag{demo_flag}")
            arguments.prompt(challenge)

            print("\nInformation filled out.")

            print("\nInformation for the challenge:")
            print(challenge)

            print("\nIs the information correct?")
            if (input("Y/n: ") or "y").lower() != "y":
                print("Exiting...")
                sys.exit(1)

        else:
            challenge = Challenge(
                name = args.name,
                slug = args.slug,
                author = args.author,
                category = args.category,
                difficulty = args.difficulty,
                type = args.type,
                instanced_type = args.instanced_type or "none",
                flag = args.flag,
                points = args.points or 1000,
                min_points = args.min_points or 100,
                description_location = args.description_location,
                handout_dir = args.handout_location
            )

            if args.type != "static":
                try:
                    if args.dockerfile_location:
                        challenge.add_dockerfile_location([ DockerfileLocation(args.dockerfile_location, args.dockerfile_context, args.dockerfile_identifier) ])
                except ValueError:
                    sys.exit(1)

        generator = Generator(challenge)
        generator.generate()


if __name__ == '__main__':
    ChallengeCreator().run()
