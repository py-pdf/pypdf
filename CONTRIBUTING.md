Please check the [documentation page dedicated to development](https://pypdf.readthedocs.io/en/stable/dev/intro.html).

## Creating issues / tickets

Please go here: https://github.com/py-pdf/pypdf/issues

Typically, you should not send e-mails. E-mails might only reach one person, and
it could go into spam or that person might be busy. Please create issues on
GitHub instead.

Please use the templates provided.

Keep in mind that although PDF has an official specification, there are tons of
variations which might require special handling. Thus, please always provide a
reproducing example file for us to work with. Otherwise, we have to guess possible
issues, leading to unnecessary overhead - especially since most of the contributions
happen during our free time.

If you already know a fix, consider opening a pull request after reporting the issue
to make life easier for everyone.

## Creating Pull Requests

We appreciate if people make PRs, but please be aware that pypdf is used by many
people. That means:

* We rarely make breaking changes and have a [deprecation process](https://pypdf.readthedocs.io/en/latest/dev/deprecations.html).
* New features, especially adding to the public interface, typically need to be
  discussed first.

Before you make bigger changes, open an issue to make the suggestion.
Note which interface changes you want to make.

After applying changes requested by a review, consider re-requesting a review to
indicate to the maintainers that they can have another look. For specific review
comments, please prefer answering them in the specific thread instead of the main
PR thread to keep references clear.

## AI Policy

You may ask AI (i.e., LLMs) for (coding) assistance. However, you should ensure
that you understand what it tells you and whether it makes sense. You are
responsible for any code you contribute.

**AI should not be used to generate comments when communicating with
maintainers**. We expect comments on our projects to be written by humans.

If you are opening an issue, we expect you to describe the problem in your own
words. Ensure that the code reproduces the issue and that the proposed solution
is not implemented already.

If you are opening a pull request, we expect you to be able to explain the
proposed changes in your own words. This includes the pull request body and
responses to questions. **Do not copy responses from the AI when replying to
questions from maintainers.** Prefer answering requests for clarification
over direct code rewrites.

Make sure to align the changes with the existing coding style and implementation
approaches. Additionally, **clearly indicate in your pull request when you used AI
and include the corresponding tool and model.**
