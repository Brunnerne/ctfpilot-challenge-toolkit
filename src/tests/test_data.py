import unittest
import sys
import json

sys.path.append('..')

from library.data import DockerfileLocation, Challenge, ChallengeFlag, Page

class TestChallenge(unittest.TestCase):
    def setUp(self):
        self.challenge = Challenge(
            enabled=True,
            name="Test Challenge",
            slug="test-challenge",
            author="Test Author",
            category="web",
            tags=["test", "example"],
            difficulty="easy",
            type="static",
            instanced_type="none",
            instanced_subdomains=["demo"],
            connection="nc example.com 1337",
            flag="ctfpilot{test_flag}",
            points=500,
            decay=100,
            min_points=50,
            description_location="description.md",
            handout_dir="files"
        )

    def test_initialization(self):
        self.assertEqual(self.challenge.name, "Test Challenge")
        self.assertEqual(self.challenge.slug, "test-challenge")
        self.assertEqual(self.challenge.author, "Test Author")
        self.assertEqual(self.challenge.category, "web")
        self.assertEqual(self.challenge.tags, ["test", "example"])
        self.assertEqual(self.challenge.difficulty, "easy")
        self.assertEqual(self.challenge.type, "static")
        self.assertEqual(self.challenge.instanced_type, "none")
        self.assertEqual(self.challenge.instanced_subdomains, ["demo"])
        self.assertEqual(self.challenge.connection, "nc example.com 1337")
        self.assertEqual(self.challenge.flag, [ChallengeFlag(flag='ctfpilot{test_flag}', case_sensitive=False)])
        self.assertEqual(self.challenge.points, 500)
        self.assertEqual(self.challenge.decay, 100)
        self.assertEqual(self.challenge.min_points, 50)
        self.assertEqual(self.challenge.description_location, "description.md")
        self.assertEqual(self.challenge.handout_dir, "files")

    def test_setters(self):
        self.challenge.set_name("New Name")
        self.assertEqual(self.challenge.name, "New Name")

        self.challenge.set_slug("new-slug")
        self.assertEqual(self.challenge.slug, "new-slug")

        self.challenge.set_author("New Author")
        self.assertEqual(self.challenge.author, "New Author")

        self.challenge.set_category("crypto")
        self.assertEqual(self.challenge.category, "crypto")

        self.challenge.set_difficulty("medium")
        self.assertEqual(self.challenge.difficulty, "medium")
        
        self.challenge.set_tags(["new", "tags"])
        self.assertEqual(self.challenge.tags, ["new", "tags"])

        self.challenge.set_type("shared")
        self.assertEqual(self.challenge.type, "shared")

        self.challenge.set_instanced_type("tcp")
        self.assertEqual(self.challenge.instanced_type, "tcp")
        
        self.challenge.set_instanced_name("new-instanced-challenge")
        self.assertEqual(self.challenge.instanced_name, "new-instanced-challenge")
        
        self.challenge.set_instanced_subdomains(["new-demo"])
        self.assertEqual(self.challenge.instanced_subdomains, ["new-demo"])
        
        self.challenge.set_connection("nc new.example.com 4444")
        self.assertEqual(self.challenge.connection, "nc new.example.com 4444")

        self.challenge.set_flag("ctfpilot{new_flag}")
        self.assertEqual(self.challenge.flag, [ChallengeFlag(flag='ctfpilot{new_flag}', case_sensitive=False)])

        self.challenge.set_points(1000)
        self.assertEqual(self.challenge.points, 1000)
        
        self.challenge.set_decay(50)
        self.assertEqual(self.challenge.decay, 50)

        self.challenge.set_min_points(100)
        self.assertEqual(self.challenge.min_points, 100)

        self.challenge.set_description_location("new_description.md")
        self.assertEqual(self.challenge.description_location, "new_description.md")

        self.challenge.set_handout_dir("new_files")
        self.assertEqual(self.challenge.handout_dir, "new_files")

    def test_add_dockerfile_location(self):
        dockerfile_location = DockerfileLocation("src/Dockerfile", "src/", "identifier")
        self.challenge.add_dockerfile_location([dockerfile_location])
        self.assertEqual(len(self.challenge.dockerfile_locations), 1)
        self.assertEqual(self.challenge.dockerfile_locations[0].location, "src/Dockerfile")

    def test_add_prerequisite(self):
        self.challenge.add_prerequisite("prerequisite-challenge")
        self.assertEqual(len(self.challenge.prerequisites), 1)
        self.assertEqual(self.challenge.prerequisites[0], "prerequisite-challenge")

    def test_missing_name(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name=None,
                slug="test-challenge",
                author="Test Author",
                category="web",
                difficulty="easy",
                type="static",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                decay=100,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )

    def test_missing_slug(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug=None,
                author="Test Author",
                category="web",
                difficulty="easy",
                type="static",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )

    def test_missing_author(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author=None,
                category="web",
                difficulty="easy",
                type="static",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )

    def test_missing_category(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category=None,
                difficulty="easy",
                type="static",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )

    def test_missing_difficulty(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category="web",
                difficulty=None,
                type="static",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )

    def test_missing_type(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category="web",
                difficulty="easy",
                type=None,
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )
            
    def test_too_long_connection(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category="web",
                difficulty="easy",
                type="static",
                instanced_type="none",
                connection="a" * 256,  # Exceeding max length of 255
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )

    def test_missing_flag(self):
        Challenge(
            enabled=True,
            name="Test Challenge",
            slug="test-challenge",
            author="Test Author",
            category="web",
            difficulty="easy",
            type="static",
            instanced_type="none",
            flag=None,
            points=500,
            min_points=50,
            description_location="description.md",
            handout_dir="files"
        )

    def test_bad_name(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="",
                slug="test-challenge",
                author="Test Author",
                category="web",
                difficulty="easy",
                type="static",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )

    def test_bad_slug(self):
        # slug field should automatically be slugified
        Challenge(
            enabled=True,
            name="Test Challenge",
            slug="Invalid Slug!",
            author="Test Author",
            category="web",
            difficulty="easy",
            type="static",
            instanced_type="none",
            flag="ctfpilot{test_flag}",
            points=500,
            min_points=50,
            description_location="description.md",
            handout_dir="files"
        )

    def test_bad_author(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="",
                category="web",
                difficulty="easy",
                type="static",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )

    def test_none_example_category(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category="invalid-category",
                difficulty="easy",
                type="static",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )

    def test_bad_category(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category="Invalid-category?",
                difficulty="easy",
                type="static",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )

    def test_bad_difficulty(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category="web",
                difficulty="invalid-difficulty",
                type="static",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )

    def test_bad_type(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category="web",
                difficulty="easy",
                type="invalid-type",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )
            
    def test_bad_tags(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category="web",
                difficulty="easy",
                type="static",
                instanced_type="none",
                tags=["invalid tag!", "okay"],
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )

    def test_bad_flag(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category="web",
                difficulty="easy",
                type="static",
                instanced_type="none",
                flag="invalid-flag",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )
    
    def test_single_flag(self):
        challenge = Challenge(
            enabled=True,
            name="Test Challenge",
            slug="test-challenge",
            author="Test Author",
            category="web",
            difficulty="easy",
            type="static",
            instanced_type="none",
            flag="ctfpilot{test_flag}",
            points=500,
            min_points=50,
            description_location="description.md",
            handout_dir="files"
        )
        self.assertEqual(challenge.flag, [ChallengeFlag(flag='ctfpilot{test_flag}', case_sensitive=False)])

    def test_multiple_flags(self):
        challenge = Challenge(
            enabled=True,
            name="Test Challenge",
            slug="test-challenge",
            author="Test Author",
            category="web",
            difficulty="easy",
            type="static",
            instanced_type="none",
            flag=["ctfpilot{test_flag1}", "ctfpilot{test_flag2}"],
            points=500,
            min_points=50,
            description_location="description.md",
            handout_dir="files"
        )
        self.assertEqual(challenge.flag, [ChallengeFlag(flag='ctfpilot{test_flag1}', case_sensitive=False), ChallengeFlag(flag='ctfpilot{test_flag2}', case_sensitive=False)])

    def test_bad_points(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category="web",
                difficulty="easy",
                type="static",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=-1,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )

    def test_bad_min_points(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category="web",
                difficulty="easy",
                type="static",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=-1,
                description_location="description.md",
                handout_dir="files"
            )
            
    def test_missing_decay(self):
        Challenge(
            enabled=True,
            name="Test Challenge",
            slug="test-challenge",
            author="Test Author",
            category="web",
            difficulty="easy",
            type="static",
            instanced_type="none",
            flag="ctfpilot{test_flag}",
            points=500,
            min_points=50,
            description_location="description.md",
            handout_dir="files"
        )

    def test_bad_decay(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category="web",
                difficulty="easy",
                type="static",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                decay=-1,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )

    def test_bad_description_location(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category="web",
                difficulty="easy",
                type="static",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="invalid_description.txt",
                handout_dir="files"
            )

    def test_bad_handout_dir(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category="web",
                difficulty="easy",
                type="static",
                instanced_type="none",
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="invalid/files/dir!"
            )
            
    def test_bad_instanced_subdomains(self):
        with self.assertRaises(ValueError):
            Challenge(
                enabled=True,
                name="Test Challenge",
                slug="test-challenge",
                author="Test Author",
                category="web",
                difficulty="easy",
                type="static",
                instanced_type="none",
                instanced_subdomains=["invalid subdomain!"],
                flag="ctfpilot{test_flag}",
                points=500,
                min_points=50,
                description_location="description.md",
                handout_dir="files"
            )

class TestChallengeFileWrite(unittest.TestCase):
    def test_str_json_output(self):
        schema_url = "http://example.com/schema.json"
        challenge = Challenge(
            enabled=True,
            name="Test Challenge",
            slug="test-challenge",
            author="Test Author",
            category="web",
            difficulty="easy",
            type="static",
            instanced_type="none",
            connection="nc example.com 1337",
            flag="ctfpilot{test_flag}",
            points=500,
            decay=100,
            min_points=50,
            description_location="description.md",
            handout_dir="files"
        )
        json_str = challenge.str_json(schema_url)
        data = json.loads(json_str)
        self.assertEqual(data["$schema"], schema_url)
        self.assertEqual(data["name"], "Test Challenge")
        self.assertEqual(data["slug"], "test-challenge")
        self.assertEqual(data["author"], "Test Author")
        self.assertEqual(data["category"], "web")
        self.assertEqual(data["difficulty"], "easy")
        self.assertEqual(data["type"], "static")
        self.assertEqual(data["instanced_type"], "none")
        self.assertEqual(data["instanced_subdomains"], [])
        self.assertEqual(data["connection"], "nc example.com 1337")
        self.assertEqual(data["flag"], [{'case_sensitive': False, 'flag': 'ctfpilot{test_flag}'}])
        self.assertEqual(data["points"], 500)
        self.assertEqual(data["decay"], 100)
        self.assertEqual(data["min_points"], 50)
        self.assertEqual(data["description_location"], "description.md")
        self.assertEqual(data["handout_dir"], "files")
        
    def test_str_json_output_multiple_flags(self):
        schema_url = "http://example.com/schema.json"
        challenge = Challenge(
            enabled=True,
            name="Test Challenge",
            slug="test-challenge",
            author="Test Author",
            category="web",
            difficulty="easy",
            type="static",
            instanced_type="none",
            flag=["ctfpilot{test_flag1}", "ctfpilot{test_flag2}"],
            points=500,
            decay=100,
            min_points=50,
            description_location="description.md",
            handout_dir="files"
        )
        json_str = challenge.str_json(schema_url)
        data = json.loads(json_str)
        self.assertEqual(data["$schema"], schema_url)
        self.assertEqual(data["name"], "Test Challenge")
        self.assertEqual(data["slug"], "test-challenge")
        self.assertEqual(data["author"], "Test Author")
        self.assertEqual(data["category"], "web")
        self.assertEqual(data["difficulty"], "easy")
        self.assertEqual(data["type"], "static")
        self.assertEqual(data["instanced_type"], "none")
        self.assertEqual(data["connection"], None)
        self.assertEqual(data["flag"], [{'case_sensitive': False, 'flag': 'ctfpilot{test_flag1}'}, {'case_sensitive': False, 'flag': 'ctfpilot{test_flag2}'}])
        self.assertEqual(data["points"], 500)
        self.assertEqual(data["decay"], 100)
        self.assertEqual(data["min_points"], 50)
        self.assertEqual(data["description_location"], "description.md")
        self.assertEqual(data["handout_dir"], "files")
    
    def test_str_json_output_multiple_flag_objects(self):
        schema_url = "http://example.com/schema.json"
        challenge = Challenge(
            enabled=True,
            name="Test Challenge",
            slug="test-challenge",
            author="Test Author",
            category="web",
            difficulty="easy",
            type="static",
            instanced_type="none",
            flag=[ChallengeFlag(flag='ctfpilot{test_flag1}', case_sensitive=True), ChallengeFlag(flag='ctfpilot{test_flag2}', case_sensitive=False)],
            points=500,
            decay=100,
            min_points=50,
            description_location="description.md",
            handout_dir="files"
        )
        json_str = challenge.str_json(schema_url)
        data = json.loads(json_str)
        self.assertEqual(data["$schema"], schema_url)
        self.assertEqual(data["name"], "Test Challenge")
        self.assertEqual(data["slug"], "test-challenge")
        self.assertEqual(data["author"], "Test Author")
        self.assertEqual(data["category"], "web")
        self.assertEqual(data["difficulty"], "easy")
        self.assertEqual(data["type"], "static")
        self.assertEqual(data["instanced_type"], "none")
        self.assertEqual(data["connection"], None)
        self.assertEqual(data["flag"], [{'case_sensitive': True, 'flag': 'ctfpilot{test_flag1}'}, {'case_sensitive': False, 'flag': 'ctfpilot{test_flag2}'}])
        self.assertEqual(data["points"], 500)
        self.assertEqual(data["decay"], 100)
        self.assertEqual(data["min_points"], 50)
        self.assertEqual(data["description_location"], "description.md")
        self.assertEqual(data["handout_dir"], "files")
    
    def test_str_json_output_special_chars(self):
        schema_url = "http://example.com/schema.json"
        challenge = Challenge(
            enabled=True,
            name="Test Challenge",
            slug="test-challenge",
            author="Test Author",
            category="web",
            difficulty="easy",
            tags=["test", "example"],
            type="static",
            instanced_type="none",
            flag="ctfpilot{test_flag'`\"}",
            points=500,
            min_points=50,
            description_location="description.md",
            handout_dir="files"
        )
        json_str = challenge.str_json(schema_url)
        data = json.loads(json_str)
        self.assertEqual(data["$schema"], schema_url)
        self.assertEqual(data["name"], "Test Challenge")
        self.assertEqual(data["slug"], "test-challenge")
        self.assertEqual(data["author"], "Test Author")
        self.assertEqual(data["category"], "web")
        self.assertEqual(data["difficulty"], "easy")
        self.assertEqual(data["tags"], ["test", "example"])
        self.assertEqual(data["type"], "static")
        self.assertEqual(data["instanced_type"], "none")
        self.assertEqual(data["connection"], None)
        self.assertEqual(data["flag"], [{'case_sensitive': False, 'flag': 'ctfpilot{test_flag\'`\"}'}])
        self.assertEqual(data["points"], 500)
        self.assertEqual(data["decay"], 75)
        self.assertEqual(data["min_points"], 50)
        self.assertEqual(data["description_location"], "description.md")
        self.assertEqual(data["handout_dir"], "files")

    def test_str_yml_output(self):
        schema_url = "http://example.com/schema.json"
        challenge = Challenge(
            enabled=True,
            name="Test Challenge",
            slug="test-challenge",
            author="Test Author",
            category="web",
            difficulty="easy",
            tags=["test", "example"],
            type="static",
            instanced_type="none",
            connection="nc example.com 1337",
            flag="ctfpilot{test_flag}",
            points=500,
            min_points=50,
            description_location="description.md",
            handout_dir="files"
        )
        yml_str = challenge.str_yml(schema_url)
        self.assertTrue(yml_str.startswith(f"# yaml-language-server: $schema={schema_url}"))
        self.assertIn("name: Test Challenge", yml_str)
        self.assertIn("slug: test-challenge", yml_str)
        self.assertIn("author: Test Author", yml_str)
        self.assertIn("category: web", yml_str)
        self.assertIn("difficulty: easy", yml_str)
        self.assertIn("tags:", yml_str)
        self.assertIn("- test", yml_str)
        self.assertIn("- example", yml_str)
        self.assertIn("type: static", yml_str)
        self.assertIn("instanced_type: none", yml_str)
        self.assertIn("connection: nc example.com 1337", yml_str)
        self.assertIn("flag:", yml_str)
        self.assertIn("- flag: ctfpilot{test_flag}", yml_str)
        self.assertIn("  case_sensitive: false", yml_str)
        self.assertIn("points: 500", yml_str)
        self.assertIn("decay: 75", yml_str)
        self.assertIn("min_points: 50", yml_str)
        self.assertIn("description_location: description.md", yml_str)
        self.assertIn("handout_dir: files", yml_str)
        
    def test_str_yml_output_multiple_flags(self):
        schema_url = "http://example.com/schema.json"
        challenge = Challenge(
            enabled=True,
            name="Test Challenge",
            slug="test-challenge",
            author="Test Author",
            category="web",
            difficulty="easy",
            type="static",
            instanced_type="none",
            flag=["ctfpilot{test_flag1}", "ctfpilot{test_flag2}"],
            points=500,
            decay=100,
            min_points=50,
            description_location="description.md",
            handout_dir="files"
        )
        yml_str = challenge.str_yml(schema_url)
        self.assertTrue(yml_str.startswith(f"# yaml-language-server: $schema={schema_url}"))
        self.assertIn("name: Test Challenge", yml_str)
        self.assertIn("slug: test-challenge", yml_str)
        self.assertIn("author: Test Author", yml_str)
        self.assertIn("category: web", yml_str)
        self.assertIn("difficulty: easy", yml_str)
        self.assertIn("type: static", yml_str)
        self.assertIn("instanced_type: none", yml_str)
        self.assertIn("flag:", yml_str)
        self.assertIn("- flag: ctfpilot{test_flag1}", yml_str)
        self.assertIn("  case_sensitive: false", yml_str)
        self.assertIn("- flag: ctfpilot{test_flag2}", yml_str)
        self.assertIn("  case_sensitive: false", yml_str)
        self.assertIn("points: 500", yml_str)
        self.assertIn("decay: 100", yml_str)
        self.assertIn("min_points: 50", yml_str)
        self.assertIn("description_location: description.md", yml_str)
        self.assertIn("handout_dir: files", yml_str)
        
    def test_str_yml_output_multiple_flag_objects(self):
        schema_url = "http://example.com/schema.json"
        challenge = Challenge(
            enabled=True,
            name="Test Challenge",
            slug="test-challenge",
            author="Test Author",
            category="web",
            difficulty="easy",
            type="static",
            instanced_type="none",
            flag=[ChallengeFlag(flag='ctfpilot{test_flag1}', case_sensitive=True), ChallengeFlag(flag='ctfpilot{test_flag2}', case_sensitive=False)],
            points=500,
            decay=100,
            min_points=50,
            description_location="description.md",
            handout_dir="files"
        )
        yml_str = challenge.str_yml(schema_url)
        self.assertTrue(yml_str.startswith(f"# yaml-language-server: $schema={schema_url}"))
        self.assertIn("name: Test Challenge", yml_str)
        self.assertIn("slug: test-challenge", yml_str)
        self.assertIn("author: Test Author", yml_str)
        self.assertIn("category: web", yml_str)
        self.assertIn("difficulty: easy", yml_str)
        self.assertIn("type: static", yml_str)
        self.assertIn("instanced_type: none", yml_str)
        self.assertIn("flag:", yml_str)
        self.assertIn("- flag: ctfpilot{test_flag1}", yml_str)
        self.assertIn("  case_sensitive: true", yml_str)
        self.assertIn("- flag: ctfpilot{test_flag2}", yml_str)
        self.assertIn("  case_sensitive: false", yml_str)
        self.assertIn("points: 500", yml_str)
        self.assertIn("decay: 100", yml_str)
        self.assertIn("min_points: 50", yml_str)
        self.assertIn("description_location: description.md", yml_str)
        self.assertIn("handout_dir: files", yml_str)

class TestChallengeFileLoad(unittest.TestCase):
    file_dir = 'tests/data'
    json_file = 'full-example.json'
    json_multi_flag_file = 'full-example-multi-flag.json'
    json_multi_flag_object_file = 'full-example-multi-flag-object.json'
    yml_file = 'full-example.yml'
    yml_multi_flag_file = 'full-example-multi-flag.yml'
    yml_multi_flag_object_file = 'full-example-multi-flag-object.yml'
    yaml_file = 'full-example.yaml'
    minimal_example_file = 'minimal-example.yml'
        
    def test_load_json(self):
        challenge = Challenge.load(f'{self.file_dir}/{self.json_file}')
        self.assertEqual(challenge.name, "Example Challenge")
        self.assertEqual(challenge.slug, "example-challenge")
        self.assertEqual(challenge.author, "John Smith")
        self.assertEqual(challenge.category, "web")
        self.assertEqual(challenge.difficulty, "easy")
        self.assertEqual(challenge.tags, ["demo", "example"])
        self.assertEqual(challenge.type, "static")
        self.assertEqual(challenge.instanced_type, "none")
        self.assertEqual(challenge.connection, "nc example.com 1337")
        self.assertEqual(challenge.flag, [ChallengeFlag(flag='ctfpilot{flag}', case_sensitive=False)])
        self.assertEqual(challenge.points, 500)
        self.assertEqual(challenge.decay, 100)
        self.assertEqual(challenge.min_points, 50)
        self.assertEqual(challenge.description_location, "demo/description.md")
        self.assertEqual(challenge.handout_dir, "handouts")
    
    def test_load_json_multi_flag(self):
        challenge = Challenge.load(f'{self.file_dir}/{self.json_multi_flag_file}')
        self.assertEqual(challenge.name, "Example Challenge Multi Flag")
        self.assertEqual(challenge.slug, "example-challenge-multi-flag")
        self.assertEqual(challenge.author, "Jane Doe")
        self.assertEqual(challenge.category, "crypto")
        self.assertEqual(challenge.difficulty, "medium")
        self.assertEqual(challenge.tags, [])
        self.assertEqual(challenge.type, "shared")
        self.assertEqual(challenge.instanced_type, "web")
        self.assertEqual(challenge.connection, None)
        self.assertEqual(challenge.flag, [ChallengeFlag(flag='ctfpilot{flag1}', case_sensitive=False), ChallengeFlag(flag='ctfpilot{flag2}', case_sensitive=False)])
        self.assertEqual(challenge.points, 1000)
        self.assertEqual(challenge.decay, 75)
        self.assertEqual(challenge.min_points, 100)
        self.assertEqual(challenge.description_location, "demo/description.md")
        self.assertEqual(challenge.handout_dir, "handouts")
    
    def test_load_json_multi_flag_object(self):
        challenge = Challenge.load(f'{self.file_dir}/{self.json_multi_flag_object_file}')
        self.assertEqual(challenge.name, "Example Challenge Multi Flag")
        self.assertEqual(challenge.slug, "example-challenge-multi-flag")
        self.assertEqual(challenge.author, "Jane Doe")
        self.assertEqual(challenge.category, "crypto")
        self.assertEqual(challenge.difficulty, "medium")
        self.assertEqual(challenge.tags, [])
        self.assertEqual(challenge.type, "shared")
        self.assertEqual(challenge.instanced_type, "web")
        self.assertEqual(challenge.connection, None)
        self.assertEqual(challenge.flag, [ChallengeFlag(flag='ctfpilot{flag1}', case_sensitive=True), ChallengeFlag(flag='ctfpilot{flag2}', case_sensitive=False)])
        self.assertEqual(challenge.points, 1000)
        self.assertEqual(challenge.decay, 75)
        self.assertEqual(challenge.min_points, 100)
        self.assertEqual(challenge.description_location, "demo/description.md")
        self.assertEqual(challenge.handout_dir, "handouts")
    
    def test_load_yml(self):
        challenge = Challenge.load(f'{self.file_dir}/{self.yml_file}')
        self.assertEqual(challenge.name, "Example Challenge")
        self.assertEqual(challenge.slug, "example-challenge")
        self.assertEqual(challenge.author, "John Smith")
        self.assertEqual(challenge.category, "web")
        self.assertEqual(challenge.difficulty, "easy")
        self.assertEqual(challenge.tags, ["demo", "example"])
        self.assertEqual(challenge.type, "static")
        self.assertEqual(challenge.instanced_type, "none")
        self.assertEqual(challenge.instanced_subdomains, ["demo"])
        self.assertEqual(challenge.connection, "nc example.com 1337")
        self.assertEqual(challenge.flag, [ChallengeFlag(flag='ctfpilot{flag}', case_sensitive=False)])
        self.assertEqual(challenge.points, 500)
        self.assertEqual(challenge.decay, 100)
        self.assertEqual(challenge.min_points, 50)
        self.assertEqual(challenge.description_location, "demo/description.md")
        self.assertEqual(challenge.handout_dir, "handouts")

    def test_load_yml_multi_flag(self):
        challenge = Challenge.load(f'{self.file_dir}/{self.yml_multi_flag_file}')
        self.assertEqual(challenge.name, "Example Challenge Multi Flag")
        self.assertEqual(challenge.slug, "example-challenge-multi-flag")
        self.assertEqual(challenge.author, "Jane Doe")
        self.assertEqual(challenge.category, "crypto")
        self.assertEqual(challenge.difficulty, "medium")
        self.assertEqual(challenge.tags, [])
        self.assertEqual(challenge.type, "shared")
        self.assertEqual(challenge.instanced_type, "web")
        self.assertEqual(challenge.connection, None)
        self.assertEqual(challenge.flag, [ChallengeFlag(flag='ctfpilot{flag1}', case_sensitive=False), ChallengeFlag(flag='ctfpilot{flag2}', case_sensitive=False)])
        self.assertEqual(challenge.points, 1000)
        self.assertEqual(challenge.decay, 75)
        self.assertEqual(challenge.min_points, 100)
        self.assertEqual(challenge.description_location, "demo/description.md")
        self.assertEqual(challenge.handout_dir, "handouts")
        
    def test_load_yml_multi_flag_object(self):
        challenge = Challenge.load(f'{self.file_dir}/{self.yml_multi_flag_object_file}')
        self.assertEqual(challenge.name, "Example Challenge Multi Flag")
        self.assertEqual(challenge.slug, "example-challenge-multi-flag")
        self.assertEqual(challenge.author, "Jane Doe")
        self.assertEqual(challenge.category, "crypto")
        self.assertEqual(challenge.difficulty, "medium")
        self.assertEqual(challenge.tags, [])
        self.assertEqual(challenge.type, "shared")
        self.assertEqual(challenge.instanced_type, "web")
        self.assertEqual(challenge.connection, None)
        self.assertEqual(challenge.flag, [ChallengeFlag(flag='ctfpilot{flag1}', case_sensitive=True), ChallengeFlag(flag='ctfpilot{flag2}', case_sensitive=False)])
        self.assertEqual(challenge.points, 1000)
        self.assertEqual(challenge.decay, 75)
        self.assertEqual(challenge.min_points, 100)
        self.assertEqual(challenge.description_location, "demo/description.md")
        self.assertEqual(challenge.handout_dir, "handouts")

    def test_load_yaml(self):
        challenge = Challenge.load(f'{self.file_dir}/{self.yaml_file}')
        self.assertEqual(challenge.name, "Example Challenge")
        self.assertEqual(challenge.slug, "example-challenge")
        self.assertEqual(challenge.author, "John Smith")
        self.assertEqual(challenge.category, "web")
        self.assertEqual(challenge.difficulty, "easy")
        self.assertEqual(challenge.tags, ["demo", "example"])
        self.assertEqual(challenge.type, "static")
        self.assertEqual(challenge.instanced_type, "none")
        self.assertEqual(challenge.instanced_subdomains, [])
        self.assertEqual(challenge.connection, "nc example.com 1337")
        self.assertEqual(challenge.flag, [ChallengeFlag(flag='ctfpilot{flag}', case_sensitive=False)])
        self.assertEqual(challenge.points, 500)
        self.assertEqual(challenge.min_points, 50)
        self.assertEqual(challenge.description_location, "demo/description.md")
        self.assertEqual(challenge.handout_dir, "handouts")
        
    def test_load_minimal_example(self):
        challenge = Challenge.load(f'{self.file_dir}/{self.minimal_example_file}')
        self.assertEqual(challenge.name, "Example Challenge")
        self.assertEqual(challenge.slug, "example-challenge")
        self.assertEqual(challenge.author, "John Smith")
        self.assertEqual(challenge.category, "web")
        self.assertEqual(challenge.difficulty, "easy")
        self.assertEqual(challenge.tags, [])
        self.assertEqual(challenge.type, "static")
        self.assertEqual(challenge.instanced_type, "none")
        self.assertEqual(challenge.connection, None)
        self.assertEqual(challenge.flag, [ChallengeFlag(flag='ctfpilot{flag}', case_sensitive=False)])
        self.assertEqual(challenge.points, 1000)
        self.assertEqual(challenge.decay, 75)
        self.assertEqual(challenge.min_points, 100)
        self.assertEqual(challenge.description_location, "description.md")
        self.assertEqual(challenge.handout_dir, "handout")

    def test_bad_file(self):
        with self.assertRaises(FileNotFoundError):
            Challenge.load(f'{self.file_dir}/invalid_challenge.json')
            
    def test_bad_file_extension(self):
        with self.assertRaises(ValueError):
            Challenge.load(f'{self.file_dir}/invalid_challenge.txt')

class TestPage(unittest.TestCase):

    def test_page_initialization(self):
        page = Page(
            enabled=True,
            slug="example-page",
            title="Example Page",
            route="/example-page",
            content="example.md",
            format="markdown",
            auth=True,
            draft=False
        )
        self.assertTrue(page.enabled)
        self.assertEqual(page.slug, "example-page")
        self.assertEqual(page.title, "Example Page")
        self.assertEqual(page.route, "/example-page")
        self.assertEqual(page.content, "example.md")
        self.assertEqual(page.format, "markdown")
        self.assertTrue(page.auth)
        self.assertFalse(page.draft)

    def test_page_setters(self):
        page = Page()
        page.set_slug("new-page")
        self.assertEqual(page.slug, "new-page")

        page.set_title("New Page Title")
        self.assertEqual(page.title, "New Page Title")

        page.set_route("/new-page")
        self.assertEqual(page.route, "/new-page")

        page.set_content("new-content.md")
        self.assertEqual(page.content, "new-content.md")

        page.set_format("html")
        self.assertEqual(page.format, "html")

        page.set_auth(True)
        self.assertTrue(page.auth)

        page.set_draft(True)
        self.assertTrue(page.draft)

    def test_page_invalid_slug(self):
        with self.assertRaises(ValueError):
            Page(slug="")

    def test_page_invalid_title(self):
        with self.assertRaises(ValueError):
            Page(title="")

    def test_page_invalid_route(self):
        with self.assertRaises(ValueError):
            Page(route="")

    def test_page_invalid_content(self):
        with self.assertRaises(ValueError):
            Page(content="invalid-content")

    def test_page_invalid_format(self):
        with self.assertRaises(ValueError):
            Page(format="invalid-format")

    def test_page_generate_dict(self):
        page = Page(
            enabled=True,
            slug="example-page",
            title="Example Page",
            route="/example-page",
            content="example.md",
            format="markdown",
            auth=True,
            draft=False
        )
        schema_location = "http://example.com/schema.json"
        page_dict = page.generate_dict(schema_location)
        self.assertEqual(page_dict["$schema"], schema_location)
        self.assertTrue(page_dict["enabled"])
        self.assertEqual(page_dict["slug"], "example-page")
        self.assertEqual(page_dict["title"], "Example Page")
        self.assertEqual(page_dict["route"], "/example-page")
        self.assertEqual(page_dict["content"], "example.md")
        self.assertEqual(page_dict["format"], "markdown")
        self.assertTrue(page_dict["auth"])
        self.assertFalse(page_dict["draft"])

    def test_page_str_json_output(self):
        schema_url = "http://example.com/schema.json"
        page = Page(
            enabled=True,
            slug="example-page",
            title="Example Page",
            route="/example-page",
            content="example.md",
            format="markdown",
            auth=True,
            draft=False
        )
        json_str = page.str_json(schema_url)
        data = json.loads(json_str)
        self.assertEqual(data["$schema"], schema_url)
        self.assertEqual(data["slug"], "example-page")
        self.assertEqual(data["title"], "Example Page")
        self.assertEqual(data["route"], "/example-page")
        self.assertEqual(data["content"], "example.md")
        self.assertEqual(data["format"], "markdown")
        self.assertTrue(data["auth"])
        self.assertFalse(data["draft"])

    def test_page_str_yml_output(self):
        schema_url = "http://example.com/schema.json"
        page = Page(
            enabled=True,
            slug="example-page",
            title="Example Page",
            route="/example-page",
            content="example.md",
            format="markdown",
            auth=True,
            draft=False
        )
        yml_str = page.str_yml(schema_url)
        self.assertTrue(yml_str.startswith(f"# yaml-language-server: $schema={schema_url}"))
        self.assertIn("slug: example-page", yml_str)
        self.assertIn("title: Example Page", yml_str)
        self.assertIn("route: /example-page", yml_str)
        self.assertIn("content: example.md", yml_str)
        self.assertIn("format: markdown", yml_str)
        self.assertIn("auth: true", yml_str)
        self.assertIn("draft: false", yml_str)

    def test_page_load_from_json(self):
        json_data = {
            "enabled": True,
            "slug": "example-page",
            "title": "Example Page",
            "route": "/example-page",
            "content": "example.md",
            "format": "markdown",
            "auth": True,
            "draft": False
        }
        page = Page.load_from_json(json_data)
        self.assertTrue(page.enabled)
        self.assertEqual(page.slug, "example-page")
        self.assertEqual(page.title, "Example Page")
        self.assertEqual(page.route, "/example-page")
        self.assertEqual(page.content, "example.md")
        self.assertEqual(page.format, "markdown")
        self.assertTrue(page.auth)
        self.assertFalse(page.draft)

    def test_page_load_from_yaml(self):
        yaml_data = {
            "enabled": True,
            "slug": "example-page",
            "title": "Example Page",
            "route": "/example-page",
            "content": "example.md",
            "format": "markdown",
            "auth": True,
            "draft": False
        }
        page = Page.load_from_yaml(yaml_data)
        self.assertTrue(page.enabled)
        self.assertEqual(page.slug, "example-page")
        self.assertEqual(page.title, "Example Page")
        self.assertEqual(page.route, "/example-page")
        self.assertEqual(page.content, "example.md")
        self.assertEqual(page.format, "markdown")
        self.assertTrue(page.auth)
        self.assertFalse(page.draft)

if __name__ == '__main__':
    print("Tests cannot be run directly. Please run test.py")