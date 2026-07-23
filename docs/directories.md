# Directory structure recommendations

In this document you will find explanations of the directories in this project,
what their purpose is and how you can use them.

 * `.github` will later contain the workflow descriptions which will instruct
   GitHub to automatically deploy your web application.
 * `.agents` contains optional agent-facing instructions and reusable skills.
   The folder `.agents/skills` is intended for generic skills that can also be
   used by other kinds of coding agents.
 * `.vscode` contains useful settings for working in VS Code.
 * `.venv` contains the locally installed libraries as setup and installed by
   `uv`.
 * `docs` contains all the development related documents in Markdown (`*.md`)
   format. You should document your architecture, your design decisions and
   possibly complex steps needed for your application in this directory. The
   folder `docs/decisions` in particular is used to document any application
   wide design decisions you made for this project.
   `docs/agent-collaboration.md` explains how students should work with coding
   agents in this template, and `docs/decision-template.md` provides a starter
   structure for decision records.
   `docs/deployment-azure-app-service-flask.md` contains optional deployment
   notes for teams that choose Flask and deployment to Azure App Service with
   the built-in Python runtime.
 * The folder `src/app` is where your Python backend code will live. The folder
   `src/app/static` will take your frontend code.

In the root directory, the following files are potentially relevant for direct
modification by a developer:

 * `.gitignore` contains a list of file and directory patterns that should be
   ignored by the version control system Git and should never be versioned.
 * `MANUAL.md` contains information related to this project template. They are
   meant for an easier start but may be removed in a later step of the project.
 * `README.md` should give people that want to get started with this project a
   first and quick overview about what this project is and how to get started.
 * `pyproject.toml` is a technical description of your project and you might
   need to edit this manually in some cases. For pure dependency management,
   for example for adding and removing packages, you can use `uv add ...` and
   `uv remove ...` and uv will automatically update `pyproject.toml` for you.
   Remember to add the modified version to Git.
 * `startup.sh` should be added if you deploy a Flask application to Azure
   App Service with the built-in Python runtime. See
   `docs/deployment-azure-app-service-flask.md` for the required content.
