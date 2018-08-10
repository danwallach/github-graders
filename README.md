# github-graders.py 

If you're using GitHub Classroom, one of the things you may need to do
is assign student submissions to graders. This project does this as a
random mapping, printing a document that you might share with your
graders on Piazza or whatever forum, with grader names and student
project hyperlinks.

## Installation

0) This project requires Python3. You may need to install that first.

1) If you haven't already done this, you'll need to `pip3 install
requests` for a necessary library.

2) Get a GitHub token with all the "Repo" privileges. You do
this on the GitHub website
[(instructions)](https://github.com/blog/1509-personal-api-tokens). 

3) Optionally, edit the `defaut_github_project` variable to reflect your
   project's name (e.g., for `https://github.com/RiceComp215`, the
   project name is `RiceComp215`). You can also install your GitHub
   API token in the `default_github_token` variable.

4) Edit the list of graders (use your graders' GitHub IDs)

5) Edit the list of users to ignore (automatically includes your
   graders, might as well include yourself as well).

## Usage

Now let's say you want to assign graders for every repo beginning with `comp215-week06`
and you've already edited in the list of graders, as specified above.
You can simply run `python3 github-graders.py --prefix comp215-week06`
and it will print out everything you need. We post this on
Piazza, with a private post visible only to the graders, and we ask
the graders to edit it to mark the students as "done" when they're
done with their grading session. (This helps us see what graders
haven't finished their work and, if necessary, assign other graders to pick up
the slack.)

Note: the output is in Markdown format, which Piazza has recently added. Select the
Markdown block before cutting-and-pasting.
