import sys
import argparse

from library.utils import Utils

class Args:
    args = None
    slug: str = ""
    subcommand = False
    
    def __init__(self, parent_parser = None):
        if parent_parser:
            self.subcommand = True
            self.parser = parent_parser.add_parser("slugify", help="Slugify a string for use in challenge slug")
        else:
            self.parser = argparse.ArgumentParser(description="Slugify a string for use in challenge slug")

        self.parser.add_argument("name", help="Name to slugify")
    
    def parse(self):
        if self.subcommand:
            self.args = self.parser.parse_args(sys.argv[2:])
        else:
            self.args = self.parser.parse_args()
        
        if not self.args.name:
            print("Name is required")
            sys.exit(1)

        self.slug = self.args.name
        
class Slugify:
    @staticmethod
    def run(name: str) -> str:
        """
        Slugify a string for use in challenge slug.
        """
        return Utils.slugify(name) or ""

class SlugifyCommand:
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
        
        args = self.args

        print(Slugify.run(args.slug))

