from git import Repo, GitCommandError, InvalidGitRepositoryError, GitError
import glob
import os
import shutil
import stat
import urllib.parse

BASE_PATH="/tmp"


class GitRepoManager:
    def __init__(self, repo_path, repo_url=None, branch="main", env=None, user_name="nobody", user_email="nobody@gmail.com"):
        self.repo_path = repo_path
        self.repo_url = repo_url
        self.branch = branch
        self.env = env or {}
        self.user_name = user_name
        self.user_email = user_email
        self.repo = None
        self.repo_name = self.get_repo_name()

    def clone_or_open(self):
        try:
            if self.repo_url and not os.path.exists(self.repo_path):
                self.repo = Repo.clone_from(
                    self.repo_url,
                    self.repo_path,
                    env=self.env,
                    single_branch=True,
                    b=self.branch
                )
            else:
                self.repo = Repo(self.repo_path)
            self._configure_user()
        except (InvalidGitRepositoryError, GitError, GitCommandError):
            raise

    def _configure_user(self):
        if self.repo:
            with self.repo.config_writer() as cw:
                cw.set_value("user", "name", self.user_name)
                cw.set_value("user", "email", self.user_email)

    def checkout_branch(self):
        try:
            self.repo.git.checkout(self.branch)
        except GitCommandError:
            self.repo.git.checkout("-b", self.branch)
            self.repo.git.push("-u", "origin", self.branch)
            self.repo.git.remote("set-branches", "--add", "origin", self.branch)
            self.repo.git.fetch("-u", "origin", f"{self.branch}:{self.branch}")

    def pull(self):
        if self.repo:
            self.repo.git.pull("origin", self.branch)

    def commit_and_push(self, message="Update",branch=None):
        self.remote_url = self.repo_url
        if self.repo:
            self.repo.git.add(A=True)
            self.repo.index.commit(message)

            # Set remote URL with PAT
            origin = self.repo.remote(name="origin")
            origin.set_url(self.remote_url)

            # Push changes
            try:
                if branch is not None:
                    origin.push(branch)
                else:
                    origin.push(self.branch)
                print(f"Pushed to {self.branch} successfully!")
            except Exception as e:
                print("Push failed:", e)

    def update_remote(self, new_url):
        self.repo.git.remote("set-url", "origin", new_url)

    def get_repo_name(self):
        return self.repo_url.split("/")[-1].split(".git")[0]



class LocalResourceManager:
    def __init__(self, base_path=BASE_PATH):
        self.base_path = base_path

    def get_repo_path(self, path_id):
        return os.path.join(self.base_path, "git_repos", str(path_id))

    def get_import_export_path(self, path_id):
        return os.path.join(self.base_path, "import_export", str(path_id))

    def resolve_wildcard_path(self, path):
        path_list = glob.glob(path)
        if path_list:
            return path_list[0]
        head, _ = os.path.split(path)
        return self.resolve_wildcard_path(head)

    def delete_tree(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)


# ---------------- Git Helpers for SSH / HTTPS ---------------- #

def get_user_private_key(user_id, sshkey=None, ssh_key_id=None):
    """Save SSH private key locally and return path"""
    if not sshkey:
        raise ValueError("SSH key not provided")  # in real case, fetch from DB/API

    ssh_dir = f"/tmp/ssh_keys/{user_id}/{ssh_key_id or 'default'}"
    os.makedirs(ssh_dir, exist_ok=True)
    key_path = os.path.join(ssh_dir, "id_rsa")

    if not os.path.exists(key_path):
        with open(key_path, "w") as f:
            f.write(sshkey)
        os.chmod(key_path, stat.S_IRWXU)

    return key_path, "ssh_user"


def generate_url_with_creds(repo_url, creds):
    """Inject username/password into HTTPS repo URL"""
    if "http" not in repo_url:
        raise ValueError("URL must be HTTPS format")
    password = urllib.parse.quote(creds["password"])
    user = creds["user_name"]
    if "@" in repo_url:
        proto, host = repo_url.split("://")
        return f"{proto}://{user}:{password}@{host.split('@')[-1]}"
    return f"{repo_url.replace('https://', f'https://{user}:{password}@')}"


def generate_git_env(git_details, user_id):
    repo_url = git_details["solution_git_repo"]
    if repo_url.startswith("http"):
        repo_url = generate_url_with_creds(repo_url, git_details["solution_git_creds"])
        git_env, user_name = {}, git_details["solution_git_creds"]["user_name"]
    else:  # SSH case
        private_key_path, user_name = get_user_private_key(
            user_id,
            git_details.get("ssh_key"),
            git_details.get("ssh_key_id")
        )
        git_env = {
            "GIT_SSH_COMMAND": f"ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i {private_key_path}"
        }
    return repo_url, git_env, user_name


# ---------------- Main Git Handler ---------------- #

class GitHandler:
    _instance = None

    def __init__(self, path_id, user_id, git_details, branch="main"):
        self.path_id = path_id
        self.user_id = user_id
        self.branch = branch
        # Generate repo_url, env, user_name automatically
        self.repo_url, self.git_env, self.user_name = generate_git_env(git_details, user_id)
        self.repo_name = self.get_repo_name()


        # Managers
        self.local_mgr = LocalResourceManager()
        self.repo_path = self.local_mgr.get_repo_path(self.repo_name)
        self.repo_mgr = GitRepoManager(
            user_email="nareaero@gmail.com",
            repo_path=self.repo_path,
            repo_url=self.repo_url,
            branch=self.branch,
            env=self.git_env,
            user_name=self.user_name
        )

        # Clone or open repo
        self.repo_mgr.clone_or_open()
        GitHandler._instance = self

    @staticmethod
    def get_instance(path_id, user_id, git_details, branch="main"):
        if GitHandler._instance and GitHandler._instance.path_id == path_id:
            return GitHandler._instance
        return GitHandler(path_id, user_id, git_details, branch)

    def branch_exists(self, branch_name):
        """
        Check if a branch exists locally or remotely.

        Args:
            branch_name (str): Name of the branch to check.

        Returns:
            bool: True if branch exists, False otherwise.
        """
        if self.repo_mgr.repo is None:
            raise ValueError("Repository not initialized")

        # Get all local branches
        local_branches = [b.name for b in self.repo_mgr.repo.branches]
        if branch_name in local_branches:
            return True

        # Get all remote branches
        remote_branches = [ref.name.split("/")[-1] for ref in self.repo_mgr.repo.remotes.origin.refs]
        if branch_name in remote_branches:
            return True

        return True

    # Delegate methods
    def pull_latest(self):
        self.repo_mgr.pull()

    def switch_branch(self):
        self.repo_mgr.checkout_branch()

    def commit_and_push(self, message="Update",branch_name=None):
        if self.branch_exists(branch_name):
            self.repo_mgr.commit_and_push(message,branch=branch_name)
        else:
            raise InvalidGitRepositoryError

    def update_remote(self, new_url):
        self.repo_mgr.update_remote(new_url)

    def get_repo_name(self):
        return self.repo_url.split("/")[-1].split(".git")[0]

    def add_files_and_push(self, file_paths, commit_message="Update files",push=False):
        """
        Add files to the repo, commit, and push.

        Args:
            file_paths (list[str] or str): Single file path or list of file paths to add.
            commit_message (str): Commit message for the changes.
        """
        if file_paths:
            if not isinstance(file_paths, list):
                file_paths = [file_paths]

            abs_paths = []
            for f in file_paths:
                if not os.path.exists(f):
                    print(f"Warning: File '{f}' does not exist and will be skipped.")
                    continue

                # Copy external file into repo root
                if not f.startswith(self.repo_path):
                    dest_path = os.path.join(self.repo_path, os.path.basename(f))
                    shutil.copy2(f, dest_path)
                    abs_paths.append(dest_path)
                else:
                    abs_paths.append(f)

            # Add files to git
            for path in abs_paths:
                self.repo_mgr.repo.git.add(path)
        else:
            # No files specified: add all changes
            self.repo_mgr.repo.git.add(A=True)

        # Commit & push
        if push:
            self.commit_and_push(commit_message)

    def create_new_branch(self, branch_name, switch_to=True):
        """
        Create a new branch and optionally switch to it.

        Args:
            branch_name (str): Name of the new branch.
            switch_to (bool): Whether to checkout the new branch after creating it.
        """
        if self.repo_mgr.repo is None:
            raise ValueError("Repository not initialized")

        try:
            # Create branch
            self.repo_mgr.repo.git.branch(branch_name)
            print(f"Branch '{branch_name}' created successfully.")

            # Optionally switch
            if switch_to:
                self.repo_mgr.repo.git.checkout(branch_name)
                print(f"Switched to branch '{branch_name}'.")
        except GitCommandError as e:
            print(f"Error creating branch '{branch_name}': {e}")

    def checkout_branch(self, branch_name):
        """
        Create a new branch and optionally switch to it.

        Args:
            branch_name (str): Name of the new branch.
            switch_to (bool): Whether to checkout the new branch after creating it.
        """
        if self.repo_mgr.repo is None:
            raise ValueError("Repository not initialized")

        try:
            self.repo_mgr.repo.git.checkout(branch_name)
            print(f"Switched to branch '{branch_name}'.")
            self.repo_mgr.branch = branch_name
        except GitCommandError as e:
            print(f"Error creating branch '{branch_name}': {e}")
