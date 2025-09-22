from git import Repo, GitCommandError

class GitHandler:
    def __init__(self, repo_path='/tmp/git_repos/recipe', branch="feature/dag", pat=None):
        self.repo = Repo(repo_path)
        self.branch = branch
        if not pat:
            raise ValueError("GitHub Personal Access Token (PAT) must be provided")
        # Embed PAT in HTTPS URL
        self.remote_url = f"https://narendraakumar:{pat}@github.com/narendraakumar/recipe.git"

    def commit_and_push(self, message="Update"):
        if self.repo:
            # Stage all changes
            self.repo.git.add(A=True)
            # Commit changes
            self.repo.index.commit(message)
            try:
                # Push using the HTTPS URL with PAT
                self.repo.git.push(self.remote_url, self.branch)
                print(f"Successfully pushed to branch '{self.branch}'")
            except GitCommandError as e:
                print("Push failed:", e.stderr)

# Usage
PAT = "token"
handler = GitHandler(repo_path='/tmp/git_repos/recipe', branch="feature/dag", pat=PAT)
handler.commit_and_push("My commit message")