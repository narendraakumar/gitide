from git_handler import GitHandler

solution_details = {
    "solution_id": "sol123",
    "solution_git_repo": "https://github.com/narendraakumar/recipe.git",
    "solution_git_creds": {
        "user_name": "narendraakumar",
        "password": "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"
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
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC5xG0v+Mj5k3YF2tbgNkvW4DVfQn8U9mYY60KS2nBhFgK0cJgUVZ/W7rbcJUf23cfH/6Fe9GJz7o/soHxEUDh5q0bZHjPJX0MM2nu/Khz5vPJ17/CX65mhvAB0NFAwIZfoW2fknkxpOGPrw7kKTd2OXePGzRyB0eEO0gA+CEFDMcCZ0C5bweRx34hkRnLwoJzs6A6mP6sL9q1gx9d1NO5BTlh+yx1ztEiatSCz7cRRSntQ3bBwbiOu503vV49RX0wPIrsCHCMuKxz9db16j7g0PKXf85qJ3Abkq6SldEqEmeE+ZYS8NSh7oMTUevcb05VQQivKfntPYAY9GARTmQIFez2dtY6tq9nApx7TtQArnpXtB6na7TXomQWsaB5jAxcdgCdL4n9rF3k/RowX8jZ5CJznmRNpZiFHZYSlna1URjwk1VSu/k+wCNZhymApFywa0AHslKgHVIgbXN+tmBtozSiHM8XeSaYA9TeyLzypLNpXyzIVvAn7Q6gffMbgS27HQ6F7Mw6qakvpkdbWwF9784U6/cg+OPjldYGam1q+b1yV6Dh8wZJAEo2QAiShaAsgKyYpYKo+la1YP2w8V3MRpmYDNuhDtMSFiLyGVSbMaGoeNZH/jWsu7GZdyyZw1NRhf7X9gMPxyFBl/wmXMuIdz8v9RRaRkR9bNoBh0AocxQ== your_email@example.com
-----END RSA PRIVATE KEY-----""",
    "ssh_key_id": "key123"
}

handler = GitHandler.get_instance("p123", "u123", solution_details, branch="feature/dag")
handler.pull_latest()
handler.switch_branch()
handler.create_new_branch("test3")

handler.checkout_branch("test3")
handler.commit_and_push("SSH test commit")