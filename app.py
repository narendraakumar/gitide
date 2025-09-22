import streamlit as st
from pathlib import Path
from git_handler import GitHandler
from streamlit_ace import st_ace
st.set_page_config(
    page_title="Git Manager",
    page_icon="https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/github-white-icon.png",  # light GitHub favicon
    layout="wide"
)


st.markdown(
    """
    <div style="background-color:#F5F5F5; padding:15px; border-radius:8px; text-align:center; margin-bottom:15px;">
        <h2 style="color:#FF6600; margin:0;">Git IDE</h2>
        <p style="color:#555555; font-size:14px; margin:5px 0 0 0;">⚡ Git Operations & Python Editor — Manage branches, edit code, commit & push seamlessly!</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -------- Sidebar: Git Config --------
st.sidebar.header("Set Git Configuration")

# Initialize session_state variables if not present
if "https_user" not in st.session_state:
    st.session_state["https_user"] = ""
if "https_password" not in st.session_state:
    st.session_state["https_password"] = ""
if "ssh_key" not in st.session_state:
    st.session_state["ssh_key"] = ""

auth_method = st.sidebar.radio("Authentication Method", ["HTTPS", "SSH"])

if auth_method == "HTTPS":
    repo_url = st.sidebar.text_input("Repo URL", "https://github.com/narendraakumar/recipe.git")
    user_name = st.sidebar.text_input("Username", value=st.session_state["https_user"])
    password = st.sidebar.text_input("Password/Token", type="password", value=st.session_state["https_password"])

    # Save in session_state
    st.session_state["https_user"] = user_name
    st.session_state["https_password"] = password

    solution_details = {
        "solution_id": "sol123",
        "solution_git_repo": repo_url,
        "solution_git_creds": {"user_name": user_name, "password": password},
    }
else:
    repo_url = st.sidebar.text_input("Repo URL", "git@github.com:narendraakumar/recipe.git")
    ssh_key = st.sidebar.text_area("SSH Private Key", value=st.session_state["ssh_key"], height=200)

    st.session_state["ssh_key"] = ssh_key

    solution_details = {
        "solution_git_repo": repo_url,
        "ssh_key": ssh_key,
    }
branch = st.sidebar.text_input("Initial Branch", "main")
project_id = "p123"
user_id = "u123"
# Initialize repo
if st.sidebar.button("Initialize Repo"):
    handler = GitHandler.get_instance(project_id, user_id, solution_details, branch=branch)
    st.session_state["handler"] = handler
    st.session_state["current_branch"] = branch
    st.sidebar.success(f"Repo initialized!")

# -------- Git Operations & Editor --------

if "handler" not in st.session_state:
    st.warning("⚠️ Please initialize the repo from the sidebar first.")
    st.stop()

handler: GitHandler = st.session_state["handler"]
repo_path = handler.repo_mgr.repo_path if hasattr(handler, "repo_mgr") else "/tmp/git_repo"

# -------- Sidebar Repo Info & Current Branch --------
try:
    repo_name = Path(handler.repo_mgr.repo.working_tree_dir).name
except Exception:
    repo_name = "Unknown Repo"

st.sidebar.subheader("Repository")
st.sidebar.info(repo_name)

try:
    current_branch = handler.repo_mgr.repo.active_branch.name
except Exception:
    current_branch = branch

st.sidebar.subheader("Current Branch")
branch_display = st.sidebar.empty()
branch_display.info(current_branch)

col1, col2, col3 = st.columns(3)

# -------- Pull Latest --------
if col1.button("Pull Latest"):
    handler.pull_latest()
    st.success("Pulled latest changes")

# -------- Create Branch --------
# -------- Create Branch --------
new_branch_input = col2.text_input("New branch name", "")

if col2.button("Create Branch"):
    if new_branch_input:
        repo = handler.repo_mgr.repo
        branch_names = [b.name for b in repo.branches]

        if new_branch_input in branch_names:
            st.error(f"Branch '{new_branch_input}' already exists!")
        else:
            handler.create_new_branch(new_branch_input)
            current_branch = handler.repo_mgr.repo.active_branch.name
            st.session_state["current_branch"] = current_branch
            branch_display.info(current_branch)
            st.success(f"✅ Branch '{new_branch_input}' created!")
    else:
        st.error("Please enter a branch name!")


repo = handler.repo_mgr.repo
branch_names = [b.name for b in repo.branches]

# Replace previous text_input with selectbox for inline suggestions
checkout_branch_input = col3.selectbox(
    "Branch to checkout",
    options=branch_names,
    index=branch_names.index(current_branch) if current_branch in branch_names else 0
)

if col3.button("Checkout Branch"):
    if checkout_branch_input:
        if checkout_branch_input in branch_names:
            handler.checkout_branch(checkout_branch_input)
            current_branch = repo.active_branch.name
            st.session_state["current_branch"] = current_branch
            branch_display.info(current_branch)
            st.success(f"Checked out to branch '{current_branch}'")
        else:
            st.error(f" Branch '{checkout_branch_input}' does not exist!")
    else:
        st.error("Please select a branch to checkout!")






# -------- Create New File --------
with st.expander("➕ Create New File"):
    file_relative_path = st.text_input(
        "File Path (relative to repo)", "new_file.py",
        help="Example: utils/helpers/my_file.py"
    )
    # new_file_content = st_ace(
    #     value="",
    #     language="python",
    #     theme="monokai",
    #     keybinding="vscode",
    #     font_size=14,
    #     tab_size=4,
    #     show_gutter=True,
    #     show_print_margin=False,
    #     wrap=True,
    #     auto_update=True,
    #     readonly=False,
    #     key="new_file_editor"
    # )
    new_file_content = st_ace(
        value="",
        language="python",
        theme="monokai",
        keybinding="vscode",
        font_size=14,
        tab_size=4,
        show_gutter=True,
        show_print_margin=False,
        wrap=True,
        auto_update=True,
        readonly=False,
        key="new_file_editor",
        min_lines=15,  # initial visible lines
        max_lines=30  # scroll appears after this many lines
    )

    if st.button("Create & Save File"):
        new_file_path = Path(repo_path) / file_relative_path
        new_file_path.parent.mkdir(parents=True, exist_ok=True)

        if new_file_path.exists():
            st.error("File already exists!")
        else:
            new_file_path.write_text(new_file_content, encoding="utf-8")
            st.success(f"Created new file: {file_relative_path}")
            # Commit new file immediately
            handler.add_files_and_push([str(new_file_path)], f"Add {file_relative_path}", True)
            st.success(f" New file '{file_relative_path}' committed & pushed!")
            st.session_state["new_file_created"] = True

# -------- File Browser + Editor --------
if st.session_state.get("new_file_created"):
    files = list(Path(repo_path).rglob("*.py"))
    st.session_state["new_file_created"] = False
else:
    files = list(Path(repo_path).rglob("*.py"))


if not files:
    st.info("No Python files found in repo.")
else:
    relative_files = [str(f.relative_to(repo_path)) for f in files]
    selected_relative_file = st.selectbox("Choose file", relative_files)

    if selected_relative_file:
        file_path = Path(repo_path) / selected_relative_file
        code = file_path.read_text(encoding="utf-8")

        # Create a unique key for st_ace based on file
        editor_key = f"editor_{selected_relative_file}"

        # Initialize session state once
        if editor_key not in st.session_state or st.session_state.get("last_selected_file") != selected_relative_file:
            st.session_state[editor_key] = code
            st.session_state["last_selected_file"] = selected_relative_file

        # # Use Ace editor (do NOT overwrite st.session_state[editor_key])
        # new_code = st_ace(
        #     value=st.session_state[editor_key],
        #     language="python",
        #     theme="monokai",
        #     keybinding="vscode",
        #     font_size=14,
        #     tab_size=4,
        #     show_gutter=True,
        #     show_print_margin=False,
        #     wrap=True,
        #     auto_update=True,
        #     readonly=False,
        #     key=editor_key
        # )
        with st.container():
            st.markdown(
                """
                <div style="max-height:400px; overflow-y:auto; border:1px solid #ddd; border-radius:5px;">
                """,
                unsafe_allow_html=True
            )

            new_code = st_ace(
                value=st.session_state[editor_key],
                language="python",
                theme="monokai",
                keybinding="vscode",
                font_size=14,
                tab_size=4,
                show_gutter=True,
                show_print_margin=False,
                wrap=True,
                auto_update=True,
                readonly=False,
                key=editor_key,
                min_lines=20,
                max_lines=40
            )

            st.markdown("</div>", unsafe_allow_html=True)

        commit_msg = st.text_input("Commit Message", "Update via app editor", key=f"commit_{selected_relative_file}")

        # Save & Commit uses the new_code returned by st_ace
        if st.button("Save & Commit"):
            file_path.write_text(new_code, encoding="utf-8")
            st.success(f"Saved {selected_relative_file}")
            handler.add_files_and_push([str(file_path)], commit_msg, True)
            st.success(f"Changes to {selected_relative_file} committed & pushed!")