import sys
import argparse
import subprocess

from library.utils import Utils
from library.data import Challenge, DockerfileLocation

class Args:
    args = None
    subcommand = False
    
    def __init__(self, parent_parser = None):
        if parent_parser:
            self.subcommand = True
            self.parser = parent_parser.add_parser("pipeline", help="Pipeline for CTF challenges")
        else:
            self.parser = argparse.ArgumentParser(description="Pipeline for CTF challenges")
        
        self.parser.add_argument("challenge", help="Challenge to run (directory for challenge - 'web/example')")
        self.parser.add_argument("registry", help="Registry to push the Docker image to")
        self.parser.add_argument("image_prefix", help="Prefix for the Docker image")
        self.parser.add_argument("--image_suffix", help="Suffix for the Docker image", default="")
    
    def parse(self):
        if self.subcommand:
            self.args = self.parser.parse_args(sys.argv[2:])
        else:
            self.args = self.parser.parse_args()

    def __getattr__(self, name):
        return getattr(self.args, name)
    
class Docker:
    def __init__(self, registry: str, image_prefix: str, image_suffix: str):
        self.registry = registry
        self.image_prefix = image_prefix
        self.image_suffix = image_suffix
    
    @staticmethod
    def build(registry: str, image_prefix: str, image_suffix: str, challenge: Challenge, dockerfile_location: DockerfileLocation):
        image_full = f"{registry}/{image_prefix}-{Utils.slugify(challenge.category)}-{challenge.slug}".lower()
        
        if dockerfile_location.identifier and dockerfile_location.identifier.lower() not in ["none", "null", ""]:
            image_full += f"-{dockerfile_location.identifier}"
        if image_suffix and image_suffix.lower() not in ["none", "null", ""]:
            image_full += f"-{image_suffix}"
            
        image_full = image_full.lower()
        
        print(f"Building Docker image \"{image_full}\"...")
        
        try:
            build_command = [
                "docker", "build",
                "-t", f"{image_full}:latest",
                "-t", f"{image_full}:{challenge.get_version()}",
                "-f", f"{Utils.get_challenge_dir(challenge.category, challenge.slug)}/{dockerfile_location.location}",
                f"{Utils.get_challenge_dir(challenge.category, challenge.slug)}/{dockerfile_location.context}"
            ]
            build_proc = subprocess.Popen(build_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            if build_proc.stdout is not None:
                for line in build_proc.stdout:
                    print(line, end="")
            build_proc.wait()
            if build_proc.returncode != 0:
                raise subprocess.CalledProcessError(build_proc.returncode, build_command)

            push_command = [
                "docker", "push", image_full, "--all-tags"
            ]
            push_proc = subprocess.Popen(push_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            if push_proc.stdout is not None:
                for line in push_proc.stdout:
                    print(line, end="")
            push_proc.wait()
            if push_proc.returncode != 0:
                raise subprocess.CalledProcessError(push_proc.returncode, push_command)
        except subprocess.CalledProcessError as e:
            print(f"Error: Command failed with exit code {e.returncode}: {e.cmd}", file=sys.stderr)
            raise e

class DockerBuild:
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
        
        args = self.args.args
        
        if not args:
            print("No arguments provided")
            sys.exit(1)
        
        challenge = args.challenge
    
        if "/" not in challenge:
            print(f"Challenge {challenge} must be in the format 'category/name'")
            exit(1)
        
        challenge_path = Utils.get_challenges_dir().joinpath(challenge)
        if not challenge_path.exists():
            print(f"Challenge {challenge} does not exist")
            sys.exit(1)

        if not challenge_path.is_dir():
            print(f"Challenge {challenge} is not a directory")
            sys.exit(1)

        print(f"Running pipeline for challenge \"{challenge}\"")
        
        print("Loading challenge data...")
        challenge = Challenge.load_dir(challenge_path)
        if not challenge:
            print("Failed to load challenge data")
            sys.exit(1)
        
        print("Data loaded successfully")
        print("")
        print("Data:")
        print(challenge)
        print("")
        
        version = challenge.get_version()
        print(f"Current version: {version}")
        print("Incrementing version...")
        version += 1
        challenge.save_version(version)
        print(f"New version: {version}")
        print("")
        print("")

        print("Starting docker process...")
        docker = Docker(args.registry, args.image_prefix, args.image_suffix)
        for dockerfile_location in challenge.dockerfile_locations:
            print(f"Building Docker image for {dockerfile_location.identifier or 'default'}...")
            Docker.build(docker.registry, docker.image_prefix, docker.image_suffix, challenge, dockerfile_location)

        print("Docker process complete")
    
if __name__ == "__main__":
    DockerBuild().run()

