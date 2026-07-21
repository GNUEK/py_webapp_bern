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

## Local deployment

If you have installed Docker locally, you can test your application in a local
deployment using the `Dockerfile`. For this you first have to build the entire
application into a Docker image:

```bash
    docker build . -t webapp
```

Now you can run this Docker image and check if your server is really starting
correctly. Use the following command. Notice that the part `webapp` needs to
match with whatever you chose when creating the image in the previous step:

```bash
    docker run -p 8000:8000 webapp
```

You should now be able to open your web browser under the URL 
http://localhost:8000 and you should be greeted with a very simple page.

## Understanding the sources

Explain any high level concepts that you are using in your software. What were
your ideas for creating the whole software? What might not be apparent from the
sources alone? You can also add diagrams, photos of whiteboards or flipcharts
or even crudly drawing napkin sketches of the core concepts of your software
when they are readable and helpful for understanding.
