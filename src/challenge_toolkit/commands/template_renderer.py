import os
import sys
import argparse
import tempfile
import shutil
from pathlib import Path

from datetime import datetime

from library.utils import Utils
from library.data import Challenge
from library.generator import Generator
from library.config import CHALLENGE_SCHEMA

class Args:
    args = None
    challenge: Challenge
    subcommand = False
    expires: int = 3600
    available: int = 0
    repo: str
    
    def __init__(self, parent_parser = None):
        if parent_parser:
            self.subcommand = True
            self.parser = parent_parser.add_parser("template", help="Render template for K8s challenge")
        else:
            self.parser = argparse.ArgumentParser(description="Render template for K8s challenge")
            
        self.parser.add_argument("renderer", help="Renderer to use for the challenge", choices=["k8s", "configmap", "clean", "handout"])
        self.parser.add_argument("challenge", help="Challenge to run (directory for challenge - 'web/example')")
        self.parser.add_argument("--expires", help="Time until challenge expires", type=int, default=3600)
        self.parser.add_argument("--available", help="Time until challenge is available", type=int, default=0)
        self.parser.add_argument("--repo", help="GitHub repository for CTFd pages in the format 'owner/repo'", default=os.getenv("GITHUB_REPOSITORY", ""))
    
    def parse(self):
        if self.subcommand:
            self.args = self.parser.parse_args(sys.argv[2:])
        else:
            self.args = self.parser.parse_args()
        
        # Parse challenge from challenge argument
        challenge_path = Utils.get_challenges_dir().joinpath(self.args.challenge)
        if not challenge_path.exists() or not challenge_path.is_dir():
            print(f"Challenge {self.args.challenge} does not exist")
            sys.exit(1)
            
        challenge = Challenge.load_dir(challenge_path)
        
        if not challenge:
            print(f"Challenge {self.args.challenge} is not a valid challenge")
            sys.exit(1)
            
        self.challenge = challenge
        
        self.expires = self.args.expires
        self.available = self.args.available
        self.repo = self.args.repo or os.getenv("GITHUB_REPOSITORY", "")
        
        if not self.repo or self.repo.strip() == "":
            print("GitHub repository is required. Please provide it via the --repo argument or the GITHUB_REPOSITORY environment variable.")
            sys.exit(1)
        
    def __getattr__(self, name):
        return getattr(self.args, name)

class Clean:
    def __init__(self, challenge: Challenge):
        self.challenge = challenge
    
    def run(self):
        path = Utils.get_k8s_dir(self.challenge.category, self.challenge.slug)
        if not os.path.exists(path):
            print(f"Challenge {self.challenge.slug} does not have a k8s directory.")
            return
        
        # Empty the k8s directory
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    os.remove(file_path)
                    print(f"Removed file: {file_path}")
                except Exception as e:
                    print(f"Error removing file {file_path}: {e}")
            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    os.rmdir(dir_path)
                    print(f"Removed directory: {dir_path}")
                except Exception as e:
                    print(f"Error removing directory {dir_path}: {e}")
        
        print(f"Cleaned instanced template for {self.challenge.slug}")

class Renderer:
    @staticmethod
    def replace_templated(key: str, value: str, content: str):
        content = content.replace("{{ " + key + " }}", value)
        content = content.replace("{{" + key + "}}", value)
        content = content.replace("{ { " + key + " } }", value)
        content = content.replace("{ {" + key + "} }", value)
        return content
    

class K8s:
    def __init__(self, challenge: Challenge):
        self.challenge = challenge
        self.generator = Generator(challenge)

    def get_template_content(self):
        template_source_path = os.path.join(Utils.get_template_dir(), "instanced-k8s-challenge.yml")
        with open(template_source_path, "r") as f:
            base_template_content = f.read()
        
        challenge_template = os.path.join(self.generator.dir_template, "k8s.yml")
        challenge_template_content = ""
        challenge_template_indented = ""
        with open(challenge_template, "r") as f:
            challenge_template_content = f.read()
            challenge_template_indented = "\n".join(["    " + line for line in challenge_template_content.splitlines()])
        
        return base_template_content, challenge_template_content, challenge_template_indented

    def render(self, args: Args):
        if not self.generator.instanced_template_source_file_exists():
            print("Instanced template source file does not exist. Critical error.")
            sys.exit(1)
        
        if not self.generator.instanced_template_file_exists():
            print("Challenge does not have a k8s template.")
            sys.exit(0)
        
        base_template_content, challenge_template, challenge_template_indented = self.get_template_content()

        # If instanced, it needs to utilize the base template for instanced challenges
        templateing_base_template = challenge_template
        if self.challenge.type == "instanced":
            templateing_base_template = base_template_content
            
        print(f"Rendering k8s template for challenge {args.challenge.slug}...")

        output_content = templateing_base_template.replace("    %%TEMPLATE%%", challenge_template_indented)

        output_content = Renderer.replace_templated("CHALLENGE_NAME", args.challenge.slug, output_content)
        output_content = Renderer.replace_templated("CHALLENGE_CATEGORY", args.challenge.category, output_content)
        output_content = Renderer.replace_templated("CHALLENGE_TYPE", args.challenge.instanced_type, output_content)
        output_content = Renderer.replace_templated("CHALLENGE_VERSION", str(args.challenge.get_version()), output_content)
        output_content = Renderer.replace_templated("CHALLENGE_EXPIRES", str(args.expires), output_content)
        output_content = Renderer.replace_templated("CHALLENGE_AVAILABLE_AT", str(args.available), output_content)
        output_content = Renderer.replace_templated("CHALLENGE_REPO", args.repo, output_content)
        
        # Create docker image name
        docker_image = f"{args.challenge.category}-{args.challenge.slug}".lower().replace(" ", "")
        output_content = Renderer.replace_templated("DOCKER_IMAGE", docker_image, output_content)

        deployment_dir = Utils.get_challenge_render_dir(args.challenge.category, args.challenge.slug)
        if not os.path.exists(deployment_dir):
            os.makedirs(deployment_dir)

        if self.challenge.type != "instanced":
            # Create helm chart template
            helm_template = os.path.join(deployment_dir, "Chart.yaml")
            with open(helm_template, "w") as f:
                f.write("apiVersion: v2\n")
                f.write(f"name: {args.challenge.slug}\n")
                semver_version = f"1.{args.challenge.get_version()}.0"
                f.write(f"version: {semver_version}\n")
                f.write(f"description: Challenge {args.challenge.slug} in category {args.challenge.category}\n")
                f.write(f"appVersion: \"{semver_version}\"\n")
                f.write(f"type: application\n")
            
            helm_values_file = os.path.join(deployment_dir, "values.yaml")
            with open(helm_values_file, "w") as f:
                f.write(f"challenge:\n")
                f.write(f"  enabled: {str(args.challenge.enabled).lower()}\n")
                f.write(f"  name: {args.challenge.slug}\n")
                f.write(f"  category: {args.challenge.category}\n")
                f.write(f"  type: {args.challenge.instanced_type}\n")
                f.write(f"  version: {args.challenge.get_version()}\n")
                f.write(f"  path: {Utils.get_challenge_dir_str(args.challenge.category, args.challenge.slug)}\n")
                f.write(f"  dockerImage: {docker_image}\n")
                f.write(f"kubectf:\n")
                f.write(f"  expires: {args.expires}\n")
                f.write(f"  availableAt: {args.available}\n")
                f.write(f"  host: example.com\n")

            deployment_dir = os.path.join(deployment_dir, "templates")

        output_file = os.path.join(deployment_dir, "k8s.yml")
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file)) 

        with open(output_file, "w") as f:
            f.write(output_content)
        
        print(f"K8s template generated at {output_file}")

class ConfigMap:
    '''
    Generate configmap for k8s, which contains the challenge json file
    '''
    configmap_template = "challenge-configmap.yml"
    
    def __init__(self, challenge: Challenge):
        self.challenge = challenge
    
    def get_template_content(self):
        template_source = self.challenge.str_json(CHALLENGE_SCHEMA)
        
        # Iterate over each line in the source, and indent it
        template_source_indented = "".join(["    " + line + "\n" for line in template_source.splitlines()])
        
        return template_source_indented
    
    def get_description(self):
        return "".join(["    " + line + "\n" for line in self.challenge.get_description().splitlines()])
    
    def render(self, args: Args):
        if not os.path.exists(Utils.get_template_dir()) or not os.path.isdir(Utils.get_template_dir()) or not os.path.exists(os.path.join(Utils.get_template_dir(), self.configmap_template)):
            print("Configmap template source file does not exist. Critical error.")
            sys.exit(1)
        
        template = os.path.join(Utils.get_template_dir(), self.configmap_template)
        template_content = ""
        with open(template, "r") as f:
            template_content = f.read()

        # Insert template content
        template_json = self.get_template_content()
        output_content = template_content.replace("    %%CONFIG%%", template_json)
        output_content = output_content.replace("    %%DESCRIPTION%%", self.get_description())
    
        # Template values in configmap
        output_content = Renderer.replace_templated("CHALLENGE_NAME", args.challenge.slug, output_content)
        output_content = Renderer.replace_templated("CHALLENGE_PATH", Utils.get_challenge_dir_str(self.challenge.category, self.challenge.slug), output_content)
        output_content = Renderer.replace_templated("CHALLENGE_REPO", args.repo, output_content)
        output_content = Renderer.replace_templated("CHALLENGE_CATEGORY", args.challenge.category, output_content)
        output_content = Renderer.replace_templated("CHALLENGE_TYPE", args.challenge.instanced_type, output_content)
        output_content = Renderer.replace_templated("CHALLENGE_VERSION", str(args.challenge.get_version()), output_content)
        output_content = Renderer.replace_templated("CHALLENGE_ENABLED", str(args.challenge.enabled).lower(), output_content)
        output_content = Renderer.replace_templated("HOST", "{{ .Values.kubectf.host }}", output_content)
        
        # Insert the current date, for knowing when the challenge was last updated
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d %H:%M:%S")
        output_content = Renderer.replace_templated("CURRENT_DATE", current_date, output_content)

        configmap_dir =Utils.get_configmap_dir(args.challenge.category, args.challenge.slug)
        if not os.path.exists(configmap_dir):
            os.makedirs(configmap_dir)
        
        helm_template = os.path.join(configmap_dir, "Chart.yaml")
        with open(helm_template, "w") as f:
            f.write("apiVersion: v2\n")
            f.write(f"name: configmap-{args.challenge.slug}\n")
            semver_version = f"1.{args.challenge.get_version()}.0"
            f.write(f"version: {semver_version}\n")
            f.write(f"description: Challenge configmap for {args.challenge.slug} in category {args.challenge.category}\n")
            f.write(f"appVersion: \"{semver_version}\"\n")
            f.write(f"type: application\n")
        
        helm_values_file = os.path.join(configmap_dir, "values.yaml")
        with open(helm_values_file, "w") as f:
            f.write(f"challenge:\n")
            f.write(f"  enabled: {str(args.challenge.enabled).lower()}\n")
            f.write(f"  name: {args.challenge.slug}\n")
            f.write(f"  category: {args.challenge.category}\n")
            f.write(f"  type: {args.challenge.instanced_type}\n")
            f.write(f"  version: {args.challenge.get_version()}\n")
            f.write(f"  path: {Utils.get_challenge_dir_str(args.challenge.category, args.challenge.slug)}\n")
            f.write(f"kubectf:\n")
            f.write(f"  expires: {args.expires}\n")
            f.write(f"  availableAt: {args.available}\n")
            f.write(f"  host: example.com\n")
        
        configmap_dir = os.path.join(configmap_dir, "templates")
        output_file = os.path.join(configmap_dir, "k8s.yml")
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file)) 
    
        with open(output_file, "w") as f:
            f.write(output_content)
    
        print(f"Configmap generated at {output_file}")

class HandoutRenderer:
    def __init__(self, challenge: Challenge):
        self.challenge = challenge
    
    def render(self):
        print(f"Rendering handout for challenge {self.challenge.slug}...")
        
        # Copy the handout directory to a temporary location
        challenge_path = Utils.get_challenge_dir(self.challenge.category, self.challenge.slug)
        
        # Check if the file directory exists
        path = Utils.get_k8s_dir(self.challenge.category, self.challenge.slug)
        files_path = os.path.join(path, "files")
        if not os.path.exists(files_path) or not os.path.isdir(files_path):
            print(f"Files directory ({files_path}) does not exist for challenge {self.challenge.slug}.")
            print(f"Creating files directory for challenge {self.challenge.slug}.")
            os.makedirs(files_path, exist_ok=True)
            # Create a .gitkeep file to ensure the directory is tracked by git
            gitkeep_path = os.path.join(files_path, ".gitkeep")
            if not os.path.exists(gitkeep_path):
                with open(gitkeep_path, "w") as f:
                    f.write("# This file is to keep the directory in git.\n")
            print(f"Files directory created at {files_path}.")
        else:
            print(f"Files directory ({files_path}) exists for challenge {self.challenge.slug}.")

        # Check if the handout directory exists
        handout_dir = self.challenge.handout_dir
        handout_path = os.path.join(challenge_path, handout_dir)
        if not os.path.exists(handout_path) or not os.path.isdir(handout_path):
            print(f"Handout directory {handout_dir} does not exist for challenge {self.challenge.slug}.")
            print("Please create the handout directory and add the necessary files, if you want to pack handout files.")
            sys.exit(0)
        
        # Create temporary directory for handout
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create structure of <category>/<slug>/handout
            temp_handout_path = os.path.join(temp_dir, f"{self.challenge.category}_{self.challenge.slug}")
            os.makedirs(temp_handout_path, exist_ok=True)
            
            # Copy files from the handout directory to the temporary directory
            handout_base = Path(handout_path).resolve()
            for item in os.listdir(handout_path):
                # Verify the item is within the handout directory using resolved paths
                source_item = handout_base / item
                try:
                    source_item_resolved = source_item.resolve()
                    # Ensure the resolved path is within the handout directory
                    source_item_resolved.relative_to(handout_base)
                except (ValueError, RuntimeError):
                    print(f"Skipping item {item} as it is outside the handout directory.")
                    continue
                
                source_item = str(source_item_resolved)
                dest_item = os.path.join(temp_handout_path, item)
                
                # Get filename
                item_filename = os.path.basename(item)
                if item_filename in ['.gitkeep', '.gitignore']:
                    # Skip .gitkeep and .gitignore files
                    continue
                
                if os.path.isdir(source_item):
                    # Copy directory
                    shutil.copytree(source_item, dest_item, dirs_exist_ok=True) 
                else:  
                    # Copy file  
                    shutil.copy2(source_item, dest_item) 
            
            # If no files are present in the handout directory, do not create a zip file
            if not os.listdir(temp_handout_path):
                print("No files found in the handout directory. Skipping zip creation.")
                return
            
            # Create a zip file of the handout directory
            handout_zip_path = os.path.join(files_path, f"{self.challenge.category}_{self.challenge.slug}")
            shutil.make_archive(handout_zip_path, 'zip', root_dir=temp_dir, base_dir=f"{self.challenge.category}_{self.challenge.slug}")
            print(f"Handout files zipped to {handout_zip_path}.zip")

        print("Handout rendered successfully for challenge:", self.challenge.slug)

class TemplateRenderer:
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
        
        if args.renderer == "clean":
            clean = Clean(args.challenge)
            clean.run()
            return
        elif args.renderer == "k8s":
            k8s = K8s(args.challenge)
            k8s.render(args)
        elif args.renderer == "configmap":
            configmap = ConfigMap(args.challenge)
            configmap.render(args)
        elif args.renderer == "handout":
            handout_renderer = HandoutRenderer(args.challenge)
            handout_renderer.render()
        else:
            print(f"Renderer {args.renderer} not supported.")

if __name__ == "__main__":
    TemplateRenderer().run()
