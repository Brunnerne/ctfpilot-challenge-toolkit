import os
import sys
import argparse

from datetime import datetime

from library.utils import Utils
from library.data import Page
from library.generator import Generator
from library.config import PAGE_SCHEMA

class Args:
    args = None
    page: Page
    subcommand = False
    repo: str
    
    def __init__(self, parent_parser = None):
        if parent_parser:
            self.subcommand = True
            self.parser = parent_parser.add_parser("page", help="Render template for CTFd pages")
        else:
            self.parser = argparse.ArgumentParser(description="Render template for CTFd pages")

        self.parser.add_argument("page", help="Page to render (directory for page - 'web/example')")
        self.parser.add_argument("--repo", help="GitHub repository for CTFd pages in the format 'owner/repo'", default=os.getenv("GITHUB_REPOSITORY", ""))
    
    def parse(self):
        if self.subcommand:
            self.args = self.parser.parse_args(sys.argv[2:])
        else:
            self.args = self.parser.parse_args()
        
        # Parse page from page argument
        page_path = Utils.get_page_dir(self.args.page)
        if not page_path.exists() or not page_path.is_dir():
            print(f"Page {self.args.page} does not exist")
            sys.exit(1)

        page = Page.load_dir(page_path)

        if not page:
            print(f"Page {self.args.page} is not a valid page")
            sys.exit(1)

        self.page = page
        self.repo = self.args.repo or os.getenv("GITHUB_REPOSITORY", "")
        
        if not self.repo or self.repo.strip() == "":
            print("GitHub repository is required. Please provide it via the --repo argument or the GITHUB_REPOSITORY environment variable.")
            sys.exit(1)

    def __getattr__(self, name):
        return getattr(self.args, name)

class PageRender:
    '''
    Generate configmap for k8s, which contains the page json file
    '''
    configmap_template = "page-configmap.yml"
    page: Page

    def __init__(self, page: Page):
        self.page = page
        self.generator = Generator(page=page)

    def run(self):
        if not self.page:
            print("No page specified")
            sys.exit(1)
        
    @staticmethod
    def replace_templated(key: str, value: str, content: str):
        content = content.replace("{{ " + key + " }}", value)
        content = content.replace("{{" + key + "}}", value)
        content = content.replace("{ { " + key + " } }", value)
        content = content.replace("{ {" + key + "} }", value)
        return content
    
    def get_template_content(self):
        template_source = self.page.str_json(PAGE_SCHEMA)

        # Iterate over each line in the source, and indent it
        template_source_indented = "".join(["    " + line + "\n" for line in template_source.splitlines()])
        
        return template_source_indented
    
    def get_content(self):
        if not self.page:
            print("No page specified")
            sys.exit(1)

        # Get the content of the page
        content = self.page.content
        
        # Check if file exists
        page_path = Utils.get_page_dir(self.page.slug)
        content_path = page_path.joinpath(content)
        
        print(f"Rendering content from {content_path}")
        
        if not content_path.exists():
            print(f"Content file {content} does not exist in page {self.page.slug}")
            sys.exit(1)
        with open(content_path, "r") as f:
            rendered_content = f.read()
        
        # Iterate over each line in the source, and indent it
        rendered_content_indented = "".join(["    " + line + "\n" for line in rendered_content.splitlines()])
        
        return rendered_content_indented
    
    def render(self, args: Args):
        if not os.path.exists(Utils.get_template_dir()) or not os.path.isdir(Utils.get_template_dir()) or not os.path.exists(os.path.join(Utils.get_template_dir(), self.configmap_template)):
            print("Configmap template source file does not exist. Critical error.")
            sys.exit(1)

        # Increment version
        version = self.page.get_version()
        print(f"Current version: {version}")
        print("Incrementing version...")
        version += 1
        self.page.save_version(version)
        print(f"New version: {version}")
        
        # Get template content
        template = os.path.join(Utils.get_template_dir(), self.configmap_template)
        template_content = ""
        with open(template, "r") as f:
            template_content = f.read()

        # Insert template content
        template_json = self.get_template_content()
        output_content_initial = template_content.replace("    %%PAGE%%", template_json)
        
        content = self.get_content()
        output_content = output_content_initial.replace("    %%CONTENT%%", content)
    
        # Template values in configmap
        output_content = self.replace_templated("PAGE_SLUG", self.page.slug, output_content)
        output_content = self.replace_templated("PAGE_NAME", self.page.slug, output_content)
        output_content = self.replace_templated("PAGE_PATH", Utils.get_page_dir_str(self.page.slug), output_content)
        output_content = self.replace_templated("PAGE_REPO", args.repo, output_content)
        output_content = self.replace_templated("PAGE_VERSION", str(args.page.get_version()), output_content)
        output_content = self.replace_templated("PAGE_ENABLED", str(args.page.enabled).lower(), output_content)
        
        # Insert the current date, for knowing when the challenge was last updated
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d %H:%M:%S")
        output_content = self.replace_templated("CURRENT_DATE", current_date, output_content)
        
        # Write the output to a file
        output_file = os.path.join(Utils.get_k8s_page_dir(args.page.slug), f"page.yml")
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file)) 
    
        with open(output_file, "w") as f:
            f.write(output_content)
    
        print(f"Configmap generated at {output_file}")

class PageCommand:
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
        
        if not args or not args.page:
            print("No page specified")
            return

        PageRender(args.page).render(args)

if __name__ == "__main__":
    PageCommand().run()