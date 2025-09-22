import json
import os
import stat
import traceback
import urllib.parse
import re
from uuid import uuid4



GIT_ACTIONS_TIMEOUT = int(os.getenv("GIT_ACTIONS_TIMEOUT", "150"))




def get_user_private_key(user_id, solution_id, sshkey=None, ssh_key_id=None):
    """
        Hitting Admin APIs to get 'ssh' details for user
        and evaluating sshkey that is associated to current solution_id
    """
    user_name = ""

    if sshkey:
        private_key = sshkey
        sshkeyid = ssh_key_id
        user_name = "super_admin"
    else:
        ssh_data_list = get_user_ssh(str(user_id))
        ssh_found, private_key, sshkeyid = find_ssh_for_user(ssh_data_list, solution_id)
        if not ssh_found:
            for ssh_data in ssh_data_list:
                if ssh_data["isDefault"] and not sshkeyid:
                    sshkeyid = ssh_data["id"]
                    private_key = ssh_data["sshKey"]
                    break

    if not private_key:
        raise InvalidUsageError("ssh key not found for the user {} with sshkeyid {}".format(user_id, sshkeyid))
    private_key_local_res = LocalResource(key="/tmp/ssh_keys/{}/{}/id_rsa".format(user_id, sshkeyid))
    if not private_key_local_res.exists():
        private_key_local_res.mkdir(parent=True)
        with private_key_local_res.open("w") as f:
            f.write(private_key)
        os.chmod(private_key_local_res.fullpath, stat.S_IRWXU)
    return private_key_local_res, user_name


def generate_url_with_creds(repo_url, solution_creds):
    if "http" not in repo_url:
        raise InvalidUsageError("url should be of http format")
    if "@" in repo_url:
        split_url = repo_url.split("@")
        first_part = split_url[0].split("//")[0]
        last_part = split_url[-1]
    else:
        split_url = repo_url.split("//")
        first_part = split_url[0]
        last_part = split_url[-1]
    password = decrypt_str(solution_creds['password'])
    password = urllib.parse.quote(password)
    new_repo_url = "{0}//{1}:{2}@{3}".format(first_part, solution_creds['user_name'], password, last_part)
    return new_repo_url

def generate_git_env(solution_details, user_id):
    repo_url = solution_details["solution_git_repo"]
    if "http" in repo_url:
        if "solution_git_creds" not in solution_details:
            raise InvalidUsageError("no credentials found for the gitapp repo!!")
        repo_url = generate_url_with_creds(repo_url, solution_details["solution_git_creds"])
        git_env = {}
        user_name = solution_details["solution_git_creds"]['user_name']
    else:
        if solution_details["solution_id"] in STORES:
            private_key_local_res, user_name = get_user_private_key(user_id, solution_details["solution_id"],
                                                                    solution_details["ssh_key"],
                                                                    solution_details["ssh_key_id"])
        else:
            private_key_local_res, user_name = get_user_private_key(user_id, solution_details["solution_id"])
        git_env = {"GIT_SSH_COMMAND": "ssh -o UserKnownHostsFile=/dev/null -o "
                                      "StrictHostKeyChecking=no -i " +
                                      private_key_local_res.fullpath}
    return repo_url, git_env, user_name


request_id = ""
