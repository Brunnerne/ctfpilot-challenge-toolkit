# CTF Pilot's Challenge Toolkit

A comprehensive CLI toolkit for CTF challenge development, deployment, and management.

The Challenge Toolkit streamlines the entire CTF challenge lifecycle, from bootstrapping new challenges with proper directory structures to building Docker images and generating Kubernetes deployment manifests. Built to work seamlessly with [CTF Pilot's infrastructure](https://github.com/ctfpilot), it enforces standardized schemas and automates repetitive tasks, letting you focus on creating great challenges instead of managing boilerplate.

## Supported CTF Pilot versions

| CTF Pilot Component                                                          | Supported Version |
| ---------------------------------------------------------------------------- | ----------------- |
| [CTF Pilot's CTF Platform (CTFp)](https://github.com/ctfpilot/ctfp)          | v1.0              |
| [CTF Pilot's Challenge Schema](https://github.com/ctfpilot/challenge-schema) | v1.0              |
| [CTF Pilot's Page Schema](https://github.com/ctfpilot/page-schema)           | v1.0              |
| [CTF Pilot's CTFd Manager](https://github.com/ctfpilot/ctfd-manager)         | v1.0              |
| [kube-ctf](https://github.com/ctfpilot/kube-ctf)                             | v1.0              |

## How to run

> [!NOTE]
> We are currently working on making it easier to use the tool.  

The current tool is only provided as the raw python files.  
Therefore, in order to run the tool, first clone this repository:

```sh
git clone https://github.com/ctfpilot/challenge-toolkit
```

In order to install required dependencies, run:

```sh
pip install -r challenge-toolkit/src/requirements.txt
```

> [!IMPORTANT]
> The tool assumes, that the current working directory is the root of a challenge repository.  
> Read more about the expected structure of a challenge repository in the **[Challenge repository structure documentation](#challenge-repository-structure)** section.

You can then run the tool using python:

```sh
python challenge-toolkit/src/ctf.py <command> [arguments] [options]
```

> [!IMPORTANT]
> Deployment templates are essential for a number of commands to work properly.

In order to use `create`, `template`, and `page` you need to copy the deployment templates into the `template/` directory of your challenge repository (In accordance with the **[Template structure](#template-structure)** section).

This can be done by running:

```sh
cp -r challenge-toolkit/template/ .
```

### Environment Variables

The toolkit supports the following optional environment variables:

| Variable            | Description                                                            | Used By            |
| ------------------- | ---------------------------------------------------------------------- | ------------------ |
| `GITHUB_REPOSITORY` | GitHub repository in format `owner/repo` (e.g., `ctfpilot/challenges`) | `template`, `page` |

### Dependencies

Currently, the following dependencies are required:

- Python 3.8 or higher
- `pyyaml` Python package
- `python-slugify` Python package
- Docker (for building challenge images with the `pipeline` command)

`pyyaml` and `python-slugify` are defined in the `requirements.txt` file.

### Including the tool in your project as a git submodule

One way to include it into your own project is to add it as a git submodule:

```sh
git submodule add https://github.com/ctfpilot/challenge-toolkit
```

To then clone your own project with the submodule included, run:

```sh
git clone --recurse-submodules <your-repo-url>
```

Or if you already have cloned your repository, run:

```sh
git submodule update --init --recursive
```

### Typical usage

The tool is typically used in three scenarios:

1. **Creating a new challenge** using the `create` command.  
   The `slugify` command may be used to create the slug for the challenge, based on the name.
2. **Building resources for a challenge**. This includes:
   1. **Building Docker images** using the `pipeline` command.
   2. **Rendering Kubernetes deployment files** using the `template` command, for each type of render, in the order of `clean`, `k8s`, `configmap`, `handout`.
3. **Rendering CTFd pages** using the `page` command.

### Configuration

The toolkit can be configured, by configuring the `src/library/config.py` file.  
This is important, if you have a custom challenge schema or page schema.

Default values:

```py
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
```

## Commands

The toolkit provides several commands to manage CTF challenges throughout their lifecycle. All commands follow the format:

```sh
python challenge-toolkit/src/ctf.py <command> [arguments] [options]
```

### Command Overview

| Command    | Purpose                                     | Key Arguments                                |
| ---------- | ------------------------------------------- | -------------------------------------------- |
| `create`   | Bootstrap a new challenge                   | Options for name, category, difficulty, etc. |
| `template` | Generate K8s files, ConfigMaps, or handouts | `<renderer>` `<challenge>`                   |
| `pipeline` | Build and tag Docker images                 | `<challenge>` `<registry>` `<image_prefix>`  |
| `page`     | Generate ConfigMaps for CTFd pages          | `<page>`                                     |
| `slugify`  | Convert strings to URL-safe slugs           | `<name>`                                     |

### `create` - Create a new challenge

Bootstrap a new challenge with the proper directory structure and template files.

**Usage:**

> [!IMPORTANT]
> The challenge will be created in the current working directory, following the challenge repository structure defined in the [Challenge repository structure](#challenge-repository-structure) section.
> The new challenge will then be located in `challenges/<category>/<slug>/`.

```sh
python challenge-toolkit/src/ctf.py create [options]
```

**Options:**

| Option                          | Description                                                                                                                                            | Default          |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------- |
| `--no-prompts`                  | Skip interactive prompts and use default/provided values                                                                                               | Interactive mode |
| `--name <name>`                 | Name of the challenge                                                                                                                                  | Prompted         |
| `--slug <slug>`                 | URL-safe identifier for the challenge                                                                                                                  | Prompted         |
| `--author <author>`             | Challenge author name                                                                                                                                  | Prompted         |
| `--category <category>`         | Challenge category                                                                                                                                     | Prompted         |
| `--difficulty <difficulty>`     | Challenge difficulty                                                                                                                                   | Prompted         |
| `--type <type>`                 | Challenge type: `static`, `shared`, or `instanced`                                                                                                     | Prompted         |
| `--instanced-type <type>`       | For instanced challenges: `none`, `web`, or `tcp`. When `web` or `tcp` is provided for a non-static challenge, deployment templates will be generated. | `none`           |
| `--flag <flag>`                 | Challenge flag (format: `FLAG{...}` or `dynamic` or `null`)                                                                                            | Prompted         |
| `--points <points>`             | Initial points for the challenge                                                                                                                       | `1000`           |
| `--min-points <points>`         | Minimum points (for dynamic scoring)                                                                                                                   | `100`            |
| `--description-location <path>` | Path to the challenge description file                                                                                                                 | `description.md` |
| `--dockerfile-location <path>`  | Path to the Dockerfile (relative to challenge directory)                                                                                               | `src/Dockerfile` |
| `--dockerfile-context <path>`   | Docker build context path                                                                                                                              | `src/`           |
| `--dockerfile-identifier <id>`  | Identifier for multiple Dockerfiles                                                                                                                    | `None`           |
| `--handout_location <path>`     | Directory containing files to hand out to participants                                                                                                 | `handout`        |

**Examples:**

```sh
# Interactive mode (recommended for first-time users)
python challenge-toolkit/src/ctf.py create

# Non-interactive mode with all parameters
python challenge-toolkit/src/ctf.py create \
  --no-prompts \
  --name "SQL Injection 101" \
  --slug "sql-injection-101" \
  --author "John Doe" \
  --category web \
  --difficulty easy \
  --type instanced \
  --instanced-type web \
  --flag "FLAG{sql_1nj3ct10n_1s_fun}" \
  --points 500 \
  --min-points 100
```

### `template` - Render Kubernetes templates

Generate Kubernetes deployment files, ConfigMaps, or handout archives for challenges.

**Usage:**

> [!IMPORTANT]
> The command should be run from the root of a challenge repository, as it relies on the challenge directory structure defined in the [Challenge repository structure](#challenge-repository-structure) section.

```sh
python challenge-toolkit/src/ctf.py template <renderer> <challenge> [options]
```

**Arguments:**

| Argument      | Description                                                              | Required |
| ------------- | ------------------------------------------------------------------------ | -------- |
| `<renderer>`  | Type of rendering: `k8s`, `configmap`, `clean`, or `handout`             | Yes      |
| `<challenge>` | Challenge path in format `category/slug` (e.g., `web/sql-injection-101`) | Yes      |

**Options:**

| Option                  | Description                                       | Default                                      |
| ----------------------- | ------------------------------------------------- | -------------------------------------------- |
| `--expires <seconds>`   | Time in seconds until challenge instance expires  | `3600` (1 hour)                              |
| `--available <seconds>` | Time in seconds until challenge becomes available | `0` (immediately)                            |
| `--repo <owner/repo>`   | GitHub repository in format `owner/repo`          | `$GITHUB_REPOSITORY` env or empty (see note) |

> [!NOTE]
> The `--repo` option defaults to the `GITHUB_REPOSITORY` environment variable. If neither is set, the command will fail. This is typically set automatically in GitHub Actions workflows.

**Renderer Types:**

- **`k8s`** - Generate Kubernetes deployment YAML files for the challenge.
  
  If the challenge is of type `instanced`, it will template from the `template/k8s.yml` file, into the `k8s/challenge/k8s.yml` file. It will wrap the challenge template into the `kube-ctf` deployment template.

  If the challenge is of type `shared` or `static`, it will template from the `template/k8s.yml` file, into the `k8s/challenge/template/k8s.yml` file, along with a full helm chart located in `k8s/challenge/`.

  It will template the following fields:
  - `CHALLENGE_NAME` - Challenge slug
  - `CHALLENGE_CATEGORY` - Challenge category
  - `CHALLENGE_TYPE` - Challenge type
  - `CHALLENGE_VERSION` - Challenge version
  - `CHALLENGE_EXPIRES` - Expiry time in seconds
  - `CHALLENGE_AVAILABLE_AT` - When the challenge becomes available
  - `DOCKER_IMAGE` - Category and slug combined to docker image. Will not follow the format produced by the `pipeline` command.

  Templating is done using `{{ VARIABLE_NAME }}` syntax.
- **`configmap`** - Generate helm chart containing challenge metadata and description, which produces a ConfigMap for the [CTF Pilot's CTFd Manager](https://github.com/ctfpilot/ctfd-manager).
  
  This will render the `challenge-configmap.yml` from the global template directory, into the `k8s/config/templates/k8s.yml` file, along with a full helm chart located in `k8s/config/`.

  It will template the following fields:
  - `CHALLENGE_NAME` - Challenge slug
  - `CHALLENGE_CATEGORY` - Challenge category
  - `CHALLENGE_REPO` - GitHub repository in format `owner/repo`, uses the `--repo` option or `GITHUB_REPOSITORY` env variable
  - `CHALLENGE_PATH` - Challenge path in format `challenges/<category>/<slug>`
  - `CHALLENGE_TYPE` - Challenge instanced type
  - `CHALLENGE_VERSION` - Challenge version
  - `CHALLENGE_ENABLED` - Whether the challenge is enabled
  - `HOST` - Hostname of challenge. Will be replaced with helm template variable `{{ .Values.kubectf.host }}`
  - `CURRENT_DATE` - Current date in `%Y-%m-%d %H:%M:%S` format

  Templating is done using `{{ VARIABLE_NAME }}` syntax.
- **`clean`** - Remove all generated Kubernetes files from the `k8s/` directory
- **`handout`** - Create a ZIP archive of files in the handout directory.  
  The created archive is stored in the `k8s/files/` directory as `<category>_<slug>.zip`. It will ignore the files `.gitkeep` and `.gitignore`.

**Examples:**

```sh
# Generate Kubernetes deployment files
python challenge-toolkit/src/ctf.py template k8s web/sql-injection-101

# Generate ConfigMap with custom expiry time (2 hours) and repo
python challenge-toolkit/src/ctf.py template configmap web/sql-injection-101 \
  --expires 7200 \
  --repo ctfpilot/ctf-challenges

# Create handout archive
python challenge-toolkit/src/ctf.py template handout web/sql-injection-101

# Clean generated files
python challenge-toolkit/src/ctf.py template clean web/sql-injection-101
```

### `pipeline` - Build and tag Docker images

Build Docker images for challenges and tag them appropriately for container registry deployment.

**Usage:**

> [!IMPORTANT]
> The command should be run from the root of a challenge repository, as it relies on the challenge directory structure defined in the [Challenge repository structure](#challenge-repository-structure) section.

```sh
python challenge-toolkit/src/ctf.py pipeline <challenge> <registry> <image_prefix> [options]
```

**Arguments:**

| Argument         | Description                                                       | Required |
| ---------------- | ----------------------------------------------------------------- | -------- |
| `<challenge>`    | Challenge path in format `category/slug` (e.g., `web/example`)    | Yes      |
| `<registry>`     | Container registry URL (e.g., `ghcr.io`, `docker.io`)             | Yes      |
| `<image_prefix>` | Prefix for Docker image names, such as the name of the repository | Yes      |

**Options:**

| Option                    | Description                     | Default |
| ------------------------- | ------------------------------- | ------- |
| `--image_suffix <suffix>` | Suffix to append to image names | None    |

**Behavior:**

- Automatically increments the challenge version
- Builds Docker images using the Dockerfile locations specified in `challenge.yml`
- Tags images with both `:latest` and `:version` tags
- Image naming: `<registry>/<prefix>-<category>-<slug>[-identifier][-suffix]`

**Examples:**

```sh
# Build and tag Docker image
python challenge-toolkit/src/ctf.py pipeline \
  web/sql-injection-101 \
  ghcr.io \
  ctfpilot/ctf-challenges

# Build with custom suffix (e.g., for staging)
python challenge-toolkit/src/ctf.py pipeline \
  web/sql-injection-101 \
  ghcr.io \
  ctfpilot/ctf-challenges \
  --image_suffix staging

# Result: ghcr.io/ctfpilot/ctf-challenges-web-sql-injection-101:latest
#         ghcr.io/ctfpilot/ctf-challenges-web-sql-injection-101:1
```

### `page` - Render CTFd pages

Generate Kubernetes ConfigMaps pages, following the [CTF Pilot's Page Schema](https://github.com/ctfpilot/page-schema).

**Usage:**

> [!IMPORTANT]
> The command should be run from the root of a challenge repository, as it relies on the challenge directory structure defined in the [Challenge repository structure](#challenge-repository-structure) section.

```sh
python challenge-toolkit/src/ctf.py page <page> [options]
```

**Arguments:**

| Argument | Description                        | Required |
| -------- | ---------------------------------- | -------- |
| `<page>` | Page path (e.g., `rules`, `about`) | Yes      |

**Options:**

| Option                | Description                              | Default                                      |
| --------------------- | ---------------------------------------- | -------------------------------------------- |
| `--repo <owner/repo>` | GitHub repository in format `owner/repo` | `$GITHUB_REPOSITORY` env or empty (see note) |

> [!NOTE]
> The `--repo` option defaults to the `GITHUB_REPOSITORY` environment variable. If neither is set, the command will fail. This is typically set automatically in GitHub Actions workflows.

**Examples:**

```sh
# Render a custom page
python challenge-toolkit/src/ctf.py page rules --repo ctfpilot/ctf-challenges

# Render about page
python challenge-toolkit/src/ctf.py page about
```

### `slugify` - Convert strings to URL-safe slugs

Utility command to convert challenge names into URL-safe slugs following the toolkit's conventions.

**Usage:**

```sh
python challenge-toolkit/src/ctf.py slugify <name>
```

**Arguments:**

| Argument | Description               | Required |
| -------- | ------------------------- | -------- |
| `<name>` | String to convert to slug | Yes      |

**Examples:**

```sh
# Convert challenge name to slug
python challenge-toolkit/src/ctf.py slugify "SQL Injection 101"
# Output: sql-injection-101

# Convert with special characters
python challenge-toolkit/src/ctf.py slugify "Web: XSS & CSRF"
# Output: web-xss-csrf
```

## Challenge repository structure

> [!IMPORTANT]
> The tool works based on the Challenge repository structure defined below. Working outside a structure like this is not supported.

The tools expect a specific directory structure, where challenges are stored in a `challenges` directory.  
Inside the `challenges` directory, challenges are divided into categories.  
Each challenge is stored in its own directory, named identically to the challenge slug.

Besides the `challenges` directory, there is a `template` directory, which contains the base templates for kubernetes deployment files.

The structure is as follows:

```txt
.
├── challenges/
│   ├── web
│   ├── forensics
│   ├── rev
│   ├── crypto
│   ├── pwn
│   ├── boot2root
│   ├── osint
│   ├── misc
│   ├── blockchain
│   └── beginner/
│       └── challenge-1
├── pages/
│   └── page-1/
├── template/
├── challenge-toolkit/
└── <other files>
```

*`pages` may be split into their own repository, if desired.*

### Challenge structure

> [!TIP]
> Challenge source code is located in the `src/` directory.  
> The main files are `challenge.yml`, `description.md` and `README.md`.

Each challenge is stored in its own directory, named identically to the challenge slug.
Within the challenge directory, there are several subdirectories and files that make up the challenge.

The subdirectory structure of a challenge is as follows:

```txt
.
├── handout/
├── k8s/
├── solution/
├── src/
├── template/
├── challenge.yml
├── description.md
├── README.md
└── version
```

- `handout/`contains the files that are handed out to the user. This may be the binary that needs to be reversed, the pcap file that needs to be analyzed, etc. The files in this directory are automatically zipped and stored in the `k8s/files/` directory as `<category>_<slug>.zip`.
- `k8s/` contains the kubernetes deployment files for the challenge. This is automatically generated and used for deploying to the CTF platform. This directory should not be modified manually, but instead use the `challenge.yml` file to specify the deployment files.
- `solution/` contains the script that is used to solve the challenge. This is filled out by the challenge creator. No further standard for the content is enforced.
- `src/` contains the source code for the challenge. It contains all the code needed for running the challenge. It may also contain any copies that needs to be handed out. Dockerfiles, python scripts, etc. lives here.
- `template/` contains the template files for the challenge. For example the kubernetes deployment files, or similar, that are rendered with the data from the `challenge.yml` file.
- `challenge.yml` contains the metadata for the challenge. This must be filled out by the challenge creator. Follows a very strict structure, which can be found in the schema file provided in the file.  
  The file may be replaced by a JSON file, as `challenge.json`.
- `description.md` contains the description of the challenge. This is the text that is shown to the user, when they open the challenge. It should be written in markdown.
- `README.md` contains the base idea and information of the challenge. May contain inspiration or other internal notes about the challenge. May also contain solution steps.
- `version` contains the version of the challenge. This is automatically updated by the `pipeline` command. Contains a single number, which is the version number of the challenge.

To learn more about the `challenge.yml` file, see the [CTF Pilot's Challenge Schema](https://github.com/ctfpilot/challenge-schema).

#### Challenges with Dockerfiles

It is very common to use Docker for challenges, as it is the core for shared and instanced challenges.

Docker images are built using the `pipeline` command.
They are built based on the Dockerfiles provided in the `challenge.yml` file.
Each Dockerfile location is relative to the individual challenge directory.

The following should be described in the `challenge.yml` file for dockerfiles, under the `dockerfile_locations` key:

- `location`: The location of the Dockerfile relative to the challenge directory. Example: `src/Dockerfile`.
- `context`: The context of the Dockerfile relative to the challenge directory. Example: `src/`.  
  Context controls where Docker looks for files to include in the build process.
- `identifier`: The identifier of the Dockerfile to suffix the docker image with. Example: `web`, `db`, `app`, `bot`.
  The identifier is used when multiple Docker images are needed for a challenge.
  *This may be left out, if only a single Dockerfile is described.*

This format follows the [CTF Pilot's Challenge Schema](https://github.com/ctfpilot/challenge-schema).

<details>
    <summary>Click to expand example</summary>
    

An example of multiple Dockerfiles, with one for the app and one for the database:

```yaml
dockerfile_locations:
  - location: src/app/Dockerfile
    context: src/app/
    identifier: app
  - location: src/db/Dockerfile
    context: src/db/
    identifier: db
```

The folder structure for this example would be:

```txt
.
└── src/
    ├── app/
    │   ├── Dockerfile
    │   └── <All other files, for the app>
    └── db/
        ├── Dockerfile
        └── <All other files for the DB>
```

</details>
<br/>

The Docker image naming convention is described in the [`pipeline` command section](#pipeline---build-and-tag-docker-images) above.

### Template structure

> [!TIP]
> The template directory contains global templates for the challenge deployment.
>
> Default templates are provided in the `challenge-toolkit/template/` directory, however they must be moved to the repository `template/` directory in order to be used.

The `template/` directory contains the base templates for the challenge deployment files.  
These templates are used to generate the actual deployment files in the `k8s/` directory, when running the `template` and `page` command.  
They are also used in the initial challenge creation, when running the `create` command.

The following templates are required:

- ConfigMap templates:
  - `challenge-configmap.yml`
  - `page-configmap.yml`
- Challenge deployment templates:
  - Web: `instanced-web-k8s.yml`
  - TCP: `instanced-tcp-k8s.yml`
- [kube-ctf](https://github.com/ctfpilot/kube-ctf) deployment template:
  - `instanced-k8s-challenge.yml`

**Configmap templates** are used to generate ConfigMaps for challenges and pages.  
**Challenge deployment templates** are used to generate the Kubernetes deployment files for challenges.
The **`kube-ctf` deployment template** is used to generate the deployment file for instanced challenges, when using the [kube-ctf](https://github.com/ctfpilot/kube-ctf) platform. Within this template, the challenge deployment template is embedded.

> [!NOTE]
> Only instanced templates are currently generated. Shared templates are not yet supported.

### Page structure

> [!NOTE]
> Pages may be stored in their own repository, if desired.

> [!TIP]
> Page content is located in the root of the page directory (e.g., `page.html` or `page.md`).  
> The main files are `page.yml` (or `page.json`) and the content file.

Each page is stored in its own directory under the `pages/` directory in the repository root.
Pages are used to create custom pages in CTFd, such as rules, about pages, or other informational content.

The subdirectory structure of a page is as follows:

```txt
.
├── k8s/
├── page.html    (or page.md, page.txt)
├── page.yml     (or page.json)
└── version
```

- `k8s/` contains the Kubernetes ConfigMap file for the page. This is automatically generated by the `page` command and should not be modified manually.
- `page.html` (or `page.md`, `page.txt`) contains the actual content of the page. The filename is specified in `page.yml` via the `content` field. The content can be in HTML or Markdown format.
- `page.yml` contains the metadata for the page. This must be filled out by the page creator. Follows a strict structure defined by the [CTF Pilot's Page Schema](https://github.com/ctfpilot/page-schema).  
  The file may be replaced by a JSON file, as `page.json`.
- `version` contains the version of the page. This is automatically updated by the `page` command and contains a single number representing the version.

## Contributing

We welcome contributions of all kinds, from **code** and **documentation** to **bug reports** and **feedback**!

Please check the [Contribution Guidelines (`CONTRIBUTING.md`)](/CONTRIBUTING.md) for detailed guidelines on how to contribute.

To maintain the ability to distribute contributions across all our licensing models, **all code contributions require signing a Contributor License Agreement (CLA)**.
You can review **[the CLA here](https://github.com/ctfpilot/cla)**. CLA signing happens automatically when you create your first pull request.  
To administrate the CLA signing process, we are using **[CLA assistant lite](https://github.com/marketplace/actions/cla-assistant-lite)**.

*A copy of the CLA document is also included in this repository as [`CLA.md`](CLA.md).*  
*Signatures are stored in the [`cla` repository](https://github.com/ctfpilot/cla).*

## License

This tool and repository is licensed under the **EUPL-1.2 License**.  
You can find the full license in the **[LICENSE](LICENSE)** file.

We encourage all modifications and contributions to be shared back with the community, for example through pull requests to this repository.  
We also encourage all derivative works to be publicly available under the **EUPL-1.2 License**.  
At all times must the license terms be followed.

For information regarding how to contribute, see the [contributing](#contributing) section above.

CTF Pilot is owned and maintained by **[The0Mikkel](https://github.com/The0mikkel)**.  
Required Notice: Copyright Mikkel Albrechtsen (<https://themikkel.dk>)

## Code of Conduct

We expect all contributors to adhere to our [Code of Conduct](/CODE_OF_CONDUCT.md) to ensure a welcoming and inclusive environment for all.
