import os

import argparse

from commands.challenge_creator import ChallengeCreator
from commands.template_renderer import TemplateRenderer
from commands.page import PageCommand
from commands.pipeline import DockerBuild 
from commands.slugify import SlugifyCommand

class Args:
    command = None
    parser = None
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Challenge Toolkit CLI")

    def print_help(self):
        if self.parser:
            self.parser.print_help()

if __name__ == "__main__":
    try:
        args = Args()
        
        if (args.parser is None):
            print("Error: Parser is not initialized.")
            exit(1)
        
        subparser = args.parser.add_subparsers(dest="command", help="Subcommand to run", title="subcommands")
        
        challengeCreator = ChallengeCreator(subparser)
        challengeCreator.register_subcommand()
        templateRenderer = TemplateRenderer(subparser)
        templateRenderer.register_subcommand()
        dockerBuild = DockerBuild(subparser)
        dockerBuild.register_subcommand()
        pageRender = PageCommand(subparser)
        pageRender.register_subcommand()
        slugify = SlugifyCommand(subparser)
        slugify.register_subcommand()

        # Get subcommand to run
        namespace = args.parser.parse_args()
        command = namespace.command
            
        # Call the appropriate tool based on the command
        if command == "create":
            challengeCreator.run()
        elif command == "template":
            templateRenderer.run()
        elif command == "pipeline":
            dockerBuild.run()
        elif command == "page":
            pageRender.run()
        elif command == "slugify":
            slugify.run()
        else:
            args.print_help()
            exit(1)
    except Exception as e:
        # Detect if we are running inside a Github runner
        if os.getenv("GITHUB_ACTIONS"):
            print(f"::error::An error occurred: {e}")
        
        raise e

