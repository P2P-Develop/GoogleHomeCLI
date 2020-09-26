# GoogleHomeCLI contribution rules

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
  The master branch holds only the source code that is stable at the time of release.
- Try to use pull requests and publishing templates as much as possible.  

### Commit manners

- Usually, do not use strange commit names except in **docs**.
- If you have a GPG key, feel free to sign it.
- If you can check it, compile it to see if it works and then commit.  
  If you are not sure, and the workflow also fails, commit the fixed changes.
  > **Note: Do not make significant changes in the fix commit.**

### See also

[Code of Conduct](CODE_OF_CONDUCT.md)