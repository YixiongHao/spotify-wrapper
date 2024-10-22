# spotify-wrapper
Gatech CS 2340 project two

Base User Story #1: As a user, I want to be able to view a presentation of the different aspects of my personal Spotify music listening tastes displayed in colorful and fun ways. 

Acceptance criteria:  • Able to parse through a Spotify account's data to generate a detailed and creative summary of the user's music listening habits and tastes • Summary must consist of at least 8 distinct "slides" (transition slides count and are encouraged) 

Base User Story #2: As a user, I would like to be able to create and login to an account that saves my previously generated Spotify wraps. 

Acceptance criteria:  • Able to create and log into an account associated with your Spotify info • Able to log out of your account • Account information is persistent (exists after exiting the website) • Provide a screen where past Spotify wraps (the entire wrap, not just a summary) can be accessed, viewed, and deleted • Provide a screen where you can delete your account 

Base User Story #3: As a user, I would like the UI to be aesthetically-pleasing and responsive. 

Acceptance criteria:  • UI matches your client TA's personal design tastes and expectations • UI is not hard-coded for a specific screen resolution, will display correctly on different laptop/monitor sizes 

Base User Story #4: As a developer, I would like to avoid security leaks by not hosting secrets like API keys on GitHub. 

Acceptance criteria:  • No secrets should be committed to GitHub • We recommend storing all secrets in a file that has been added to your .gitignore to prevent accidental commits 

**Additional user stories:**

1. As a user, I would like to be able to invite a friend to join a Duo-Wrapped that
displays and compares both of our tastes in a creative combined way.
a. 8 points
b. +2 points for saving the Duo-Wrapped

2. As a user, I would like for a LLM API to dynamically describe how someone who
listens to my kind of music tends to act/think/dress during my Spotify Wrapped.
a. 3 points
b. +1 point if you use the LLM API to compare your taste with a friend's during a
Duo-Wrapped
c. See the payment disclaimer!

5. As a user, I would like to be able to hear clips from some of my top songs play during
my Spotify Wrapped
a. 3 points
b. +1 point for integrating music playback into Duo-Wrapped

6. As a user, I would like to create Spotify Wraps over short, medium, and long terms of
my listening history (each of these options must be distinguishable when saved)
a. 2 points

9. As a developer, I would like a GitHub Actions CI/CD pipeline to verify that my changes
build and are formatted correctly (according to pylint or pep8) and to prevent PRs
with bad changes from being merged into main
a. 2 points
b. +5 points for integrating code coverage libraries into the CI pipeline that
prevent the merging of PRs with less than 80% code coverage
Tip: We highly recommend starting this user story early and iteratively
adding new unit tests with each new PR
Note: your codebase must meet or exceed this coverage goal during
demo time to qualify. Your unit tests must also be non-trivial, as we
will not accept purposeless tests.

13. As a developer, I would like to run my Django website on a hosting service (like
Heroku) so anyone can access my Spotify Wrapped application
a. 5 points
b. See the payment disclaimer!

16. As a developer, I would like all functions to have proper documentation so I can
easily understand them at a glance (use docstrings for Python functions and JSDoc
for JavaScript functions)
a. 1 point

17. As a front-end developer, I would like to have a wireframe-flow diagram on Figma or
Balsamiq for all planned screens that clearly guide me in implementing the website's
UI.
a. 1 point
b. Note 1: to earn the point for this story, you must show your finalized UI flow
diagram and Figma wireframes to your TA by the end of sprint 1
c. Note 2: This is what we refer to as top-down software development.
