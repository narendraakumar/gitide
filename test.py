from git_handler import GitHandler

solution_details = {
    "solution_id": "sol123",
    "solution_git_repo": "gitrepo link",
    "solution_git_creds": {
        "user_name": "username",
        "password": "enterpassword"
    }
}

handler = GitHandler.get_instance("p123", "u123", solution_details, branch="feature/dag")
handler.pull_latest()
# handler.create_new_branch("test")
handler.checkout_branch("test")
handler.add_files_and_push(["/Users/narendrakumar/Downloads/mahhima left thumb.jpg"],"mess",True)
handler.commit_and_push("HTTPS test commit")




solution_details = {
    "solution_git_repo": "git@github.com:narendraakumar/recipe.git",
    "ssh_key": """-----BEGIN RSA PRIVATE KEY-----
    write ssh key here
-----END RSA PRIVATE KEY-----""",
    "ssh_key_id": "key123"
}

handler = GitHandler.get_instance("p123", "u123", solution_details, branch="feature/dag")
handler.pull_latest()
handler.switch_branch()
handler.create_new_branch("test3")

handler.checkout_branch("test3")
handler.commit_and_push("SSH test commit")