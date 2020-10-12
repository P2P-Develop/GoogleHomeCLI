# GoogleHomeCLI contribution rules

[Overview](README-en.md#overview) | [Usage](README-en.md#usage) | [Commands](README-en.md#commands) | [Configuration](README-en.md#configuration) | Contributing | [Security](SECURITY.md) | [Package requirement](../requirements.txt) | [Thanks](README-en.md#thanks)

<details>
<summary>Table of Contents</summary>

- [GoogleHomeCLI contribution rules](#googlehomecli-contribution-rules)
  - [Overview](#overview)
    - [Issue, Pull Request manners](#issue-pull-request-manners)
    - [Commit manners](#commit-manners)
    - [See also](#see-also)

</details>

日本語の貢献ルールは[こちら](CONTRIBUTING-ja.md)。

## Overview

this repository has established some rules to properly contribute as a GoogleHomeCLI contributor.

### Issue, Pull Request manners

- Try to minimize duplicate issue.
  The duplicate issue has a \[duplicate\] label and a reference to the issue, so if you notice it, close it.
- When asking questions in Issue, keep in mind **smart questions**.
  Please use the \[question\] label when asking a question.
- If you cannot modify `develop` directly, please create a pull request from the **forked branch**.
  this repository has two branches, `master` and `develop`.
- Be sure to select the `develop` as the basis for your pull request.
  `master` holds only the source code that is stable at the time of release.
- Try to use pull requests and publishing templates as much as possible.

### Commit manners

- If you have a GPG key, feel free to sign it.
- If you check syntax, then commit.
  If you are not sure, commit the fixed changes.
  > **Note: Do not make significant changes in the fix commit.**

### See also

[Code of Conduct](CODE_OF_CONDUCT.md)
