This document contains additional instructions about how to use this Python
project template.

# Getting Started in VSCode

Before starting, make sure you have the following VS Code extensions installed:

  * "Python" for general Python support. Extension id `ms-python.python`
  * "Black Formatter" for automatic formatting of Python code. Extension id `ms-python.black-formatter`

To get an initial virtual environment for your project, perform the following
steps:

  1. Type `Ctrl-Shift-P` and enter "Python: Create Environment...", hit the
     `Enter` key
  2. Choose `Venv` for the "environment tpye" if asked
  3. Choose your installed Python interpreter
  4. Tick the checkbox for installing the dependencies in `requirements.txt`
  5. Wait for the "Creating environment" step to complete

With the first saving of a Python file, you might see a message box saying that
"You have the Black formatter extension installed, ...". For this, choose "Yes"
to use the automatic code formatting feature.

The full tutorial to get started with Python under VSCode can be found here:
https://code.visualstudio.com/docs/python/python-tutorial

# Handin your solution

You can either handin your source code by submitting something called a Git
bundle. The section "Submission via Moodle or other LMS" explains how you
can create such a bundle.

Alternatively you can also share your repository with the lecturer.

Please make sure, you check the following points before handing in your
solution code:

* [ ] Have you included any Python standard libraries in `requirements.txt`?
      Libraries like `sys`, `os`, `pathlib` etc. are already part of the
      standard Python installation and must not be included in the
      `requirements.txt` file. Please remove them before submission.
* [ ] Does your project refer to absolute directories?
      Your colleagues and your lecturer might download your source code into
      different directories than you did. Make sure, you use project-relative
      paths when referencing resources in your project, such as pictures or
      data files.
* [ ] Does your README.md still contain text between `<` and `>`?
      This text is meant as placeholders. Please replace this text including
      the `<` and `>` characters with your own text.

## Submission via Moodle or other LMS

From the root directory of your project run the following git command:

    git bundle create <projectname>.bundle --all

Now you can simply upload the newly created file `<projectname>.bundle` to
Moodle.

Make sure you replace `<projectname>` in the above examples with a name that
identifies your own project.

### Using the provided VS Code task

Alternatively you can also use the VS Code task "Bundle for Submission" by
following these steps:

  1. Type `Ctrl-Shift-P` and enter "Tasks: Run Tasks", hit the `Enter` key
  2. Select the task "Bundle for Submission" and hit the `Enter` key

Now you should find a `.bundle` file in your project folder that is named
with your project folder name. This can be submitted to Moodle.

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
