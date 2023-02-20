This is a modified version of [`tempita`](https://github.com/agramfort/tempita):

1. I dropped any support for python 2.
2. I rewrote test module (`tempita/tests/test_tempita.py`) using `pytest`.
3. All necessary things, including the tests, are included in a single folder (`tempita/`). You may just copy this folder and include it into your package to drop any external dependency. (N.B. `tempita` uses MIT license)

I did this because the original package is not maintained (even the bitbucket repo is removed) while I cannot install it on py310 as of 2023 Feb (using `conda install`).

Please use this modified version at your own risk.


# Original README
Tempita
-------
A small templating language for text substitution, originally
authored by [Ian Bicking](https://bitbucket.org/ianb).

It isn't intended to be the Next Big Thing in templating, just a
handy little templating language for when a project outgrows
string.Template or {} substitution.

It's small, it embeds Python in strings, and it doesn't do much else.

You can read about the language, the interface and that's it, there's
nothing more to learn about it.

You can install the original 0.5 from the
[bitbucket repository](https://bitbucket.org/ianb/tempita) with:

    easy_install Tempita==dev

Note from gjhiggins
-------------------

I transmigrated this to GitHub in order to take advantage of travis-ci
continuous integration and took the opportunity to give the py3 compat
and tests a buffing (March 2013).

[![Build Status](https://travis-ci.org/gjhiggins/tempita.png?branch=master)](https://travis-ci.org/gjhiggins/tempita)