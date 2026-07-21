This document contains additional instructions about how to use this Python
project template.

# Getting Started in VSCode

When opening this project the first time with VS Code, you might see suggestions
for extensions to be installed. It is recommended to let VS Code install them
as they can be helpful for your basic development needs when programming with
Python.

**IMPORTANT** VS Code will also inform you that this project has an automatic
task configured which would be run when opening this project the first time.
If you don't want to run the `uv sync` command manually in the terminal, you can
allow VS Code to run this automatically.

# Handin your solution

To handin your solution, share your repository with the lecturers. Invite them
as Developer on your GitHub repository.

Please make sure, you check the following points before handing in your
solution code:

* [ ] Have you included any Python standard libraries in `pyproject.toml`?
      Libraries like `sys`, `os`, `pathlib` etc. are already part of the
      standard Python installation and must not be included in the
      `pyproject.toml` file. Please remove them before submission.
* [ ] Does your project refer to absolute directories?
      Your colleagues and your lecturer might download your source code into
      different directories than you did. Make sure, you use project-relative
      paths when referencing resources in your project, such as pictures or
      data files.
* [ ] Does your README.md still contain text between `<` and `>`?
      This text is meant as placeholders. Please replace this text including
      the `<` and `>` characters with your own text.

# FAQ

## Why can't I commit my source code?

Make sure, you create your source code outside of an "ignored" directory.
The folder `.vscode`, with the exception of a few files, is excluded from
version control with Git. If you place your source code in that folder,
it will not show up in the "Source Control" menu in VSCode. Instead place
it in the main directory or in a new directory.

## What is the purpose of the .vscode folder?

This folder contains additional settings for VSCode. Amongst them are
additional (build-) tasks and settings for code formatting for your
project. You can ignore this folder and all contained files for your
own projects.
