!! Change this document for your own project by removing the placeholder text, adding your own text, adding helpful sections etc. etc. !!

# <Project Title>

In a few sentences describe what your project is trying to solve.

You can use [GitHub markdown
notation](https://docs.github.com/en/github/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
or [GitLab markdown notation](https://docs.gitlab.com/ee/user/markdown.html) in
case you are using one of these platforms. This will give a nicely formatted
documentation when looking at your project online.

## Get started

Explain what the user has to type to get started with your solution. Which one
is the main Python file? In the simplest case, this could look something like
this:

```bash
    uv run gunicorn app:app
```

or on a Windows host

```powershell
    uv run waitress-serve app:app
```

In other cases the user might have to install some project dependencies first
and has to run something like this (a pyproject.toml file is also included in
the project template):

``
    uv sync
``

## Understanding the sources

Explain any high level concepts that you are using in your software. What were
your ideas for creating the whole software? What might not be apparent from the
sources alone? You can also add diagrams, photos of whiteboards or flipcharts
or even crudly drawing napkin sketches of the core concepts of your software
when they are readable and helpful for understanding.
