## Technology stack

This project represents a web application with a backend and a frontend part.
The backend is to be kept completely in Python. The frontend stack can be chosen
freely.

 * We use `uv` for any Python related tasks

## Files and directories

 * Check `docs/directories.md` for the recommended directory structure.
 * In case Django is used, the entire `src/` directory maybe adapted for Djangos
   directory conventions and the `app/` directory may be removed or ignored.

## Design guidelines

This is a project that is to be developed in the course of a master degree in
business informatics. The focus is on exploring and learning about all the parts
involved in running a full web application rather than building a fully
productive, scalable and long-term maintainable application. The created
elements should be easy to understand.

 * When discussing design options, start with the simpler options; for example
   suggest to start with Flask rather than Django, suggest vanilla JavaScript,
   HTMX or Alpine.js rather than going straight for full fledged solutions like
   Angular or React. Accept more complex solutions once the developers made it
   clear that they are needed and they understand the implications.
 * Document architectural design decisions that were discussed with the
   developers in the folder `docs/decisions`. Use a new file for every decision
   and use and continuous numbering scheme in the form
   `0001-framework-choice.md`.