# Project Governance

This document describes how the pypdf project is managed. It describes the
different actors, their roles, and the responsibilities they have.

## Terminology

* The **project** is pypdf - a free and open-source pure-python PDF library
capable of splitting, merging, cropping, and transforming the pages of PDF files.
  It includes the [code, issues, and discussions on GitHub](https://github.com/py-pdf/pypdf),
  and [the documentation on ReadTheDocs](https://pypdf.readthedocs.io/en/latest/),
  [the package on PyPI](https://pypi.org/project/pypdf/), and
  [the website on GitHub](https://py-pdf.github.io/pypdf/dev/bench/).
* A **maintainer** is a person who has technical permissions to change one or
  more part of the projects. It is a person who is driven to keep the project running
  and improving.
* A **contributor** is a person who contributes to the project. That could be
  through writing code - in the best case through forking and creating a pull
  request, but that is up to the maintainer. Other contributors describe issues,
  help to ask questions on existing issues to make them easier to answer,
  participate in discussions, and help to improve the documentation. Contributors
  are similar to maintainers, but without technial permissions.
* A **user** is a person who imports pypdf into their code. All pypdf users
  are developers, but not developers who know the internals of pypdf. They only
  use the public interface of pypdf. They will likely have less knowledge about
  PDF than contributors.
* The **community** is all of that - the users, the contributors, and the maintainers.


## Governance, Leadership, and Steering pypdf forward

pypdf is a free and open source project with over 100 contributors and likely
(way) more than 1000 users.

As pypdf does not have any formal relationship with any company and no funding,
all the work done by the community are voluntary contributions. People don't
get paid, but choose to spend their free time to create software of which
many more are profiting. This has to be honored and respected.

Despite such a big community, the project was dormant from 2016 to 2022.
There were still questions asked, issues reported, and pull requests created.
But the maintainer didn't have the time to move pypdf forward. During that
time, nobody else stepped up to become the new maintainer.

For this reason, pypdf has the **Benevolent Dictator**
governance model. The benevolent dictator is a maintainer with all technical permissions -
most importantly the permission to push new pypdf versions on PyPI.

Being benevolent, the benevolent dictator listens for decisions to the community and tries
their best to make decisions from which the overall community profits - the
current one and the potential future one. Being a dictator, the benevolent dictator always has
the power and the right to make decisions on their own - also against some
members of the community.

As pypdf is free software, parts of the community can split off (fork the code)
and create a new community. This should limit the harm a bad benevolent dictator can do.


## Project Language

The project language is (american) English. All documentation and issues must
be written in English to ensure that the community can understand it.

We appreciate the fact that large parts of the community don't have English
as their mother tongue. We try our best to understand others -
[automatic translators](https://translate.google.com/) might help.


## Expectations

The community can expect the following:

* The **benevolent dictator** tries their best to make decisions from which the overall
  community profits. The benevolent dictator is aware that his/her decisions can shape the
  overall community. Once the benevolent dictator notices that she/he doesn't have the time
  to advance pypdf, he/she looks for a new benevolent dictator. As it is expected
  that the benevolent dictator will step down at some point of their choice
  (hopefully before their death), it is NOT a benevolent dictator for life
  (BDFL).
* Every **maintainer** (including the benevolent dictator) is aware of their permissions and
  the harm they could do. They value security and ensure that the project is
  not harmed. They give their technical permissions back if they don't need them
  any longer. Any long-time contributor can become a maintainer. Maintainers
  can - and should! - step down from their role when they realize that they
  can no longer commit that time. Their contribution will be honored in the
  {doc}`history`.
* Every **contributor** is aware that the time of maintainers and the benevolent dictator is
  limited. Short pull requests that briefly describe the solved issue and have
  a unit test have a higher chance to get merged soon - simply because it's
  easier for maintainers to see that the contribution will not harm the overall
  project. Their contributions are documented in the git history and in the
  public issues. [Let us know](https://github.com/py-pdf/pypdf/discussions/798)
  if you would appreciate something else!
* Every **community member** uses a respectful language. We are all human, we
  get upset about things we care and other things than what's visible on the
  internet go on in our live. pypdf does not pay its contributors - keep all
  of that in mind when you interact with others. We are here because we want to
  help others.


### Issues and Discussions

An issue is any technical description that aims at bringing pypdf forward:

* Bugs tickets: Something went wrong because pypdf developers made a mistake.
* Feature requests: pypdf does not support all features of the PDF specifications.
  There are certainly also convenience methods that would help users a lot.
* Robustness requests: There are many broken PDFs around. In some cases, we can
  deal with that. It's kind of a mixture between a bug ticket and a feature
  request.
* Performance tickets: pypdf could be faster - let us know about your specific
  scenario.

Any comment that is in those technial descriptions which is not helping the
discussion can be deleted. This is especially true for "me too" comments on bugs
or "bump" comments for desired features. People can express this with 👍 / 👎
reactions.

[Discussions](https://github.com/py-pdf/pypdf/discussions) are open. No comments
will be deleted there - except if they are clearly unrelated spam or only
try to insult people (luckily, the community was very respectful so far 🤞)


### Releases

The maintainers follow [semantic versioning](https://semver.org/). Most
importantly, that means that breaking changes will have a major version bump.

Be aware that unintentional breaking changes might still happen. The pypdf
maintainers do their best to fix that in a timely manner - please
[report such issues](https://github.com/py-pdf/pypdf/issues)!


## People

* Martin Thoma is benevolent dictator since April 2022.
* Maintainers:
    * Matthew Stamy (mstamy2) was the benevolent dictator for a long time.
      He still is around on GitHub once in a while and has permissions on PyPI and GitHub.
    * Matthew Peveler (MasterOdin) is a maintainer on GitHub.
