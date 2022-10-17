<img src="./logo.png" width="125" height="125" align="right" />

# `__doc__` for [RustPython](https://rustpython.github.io/)

This is the `__doc__` attributes generator for objects written in RustPython.

It's composed of two parts of:

- the `generate_docs.py` script that extracts the `__doc__` attributes from CPython to `docs.inc.rs`
- the `rustpython-doc` rust crate that uses the `docs.inc.rs` file to create a documentation Database.

This documentation database is then used by macros `pymodule` and `pyclass` macros of the rustpython-derive crate to automatically add the `__doc__` attribute.

The `docs.inc.rs` database file can be generated with

    $ python -m venv gendocs
    $ source gendocs/bin/activate
    $ python -I generate_docs.py <path_to_RustPython> docs.inc.rs
    $ deactivate

or using docker

    $ docker pull python:slim
    $ docker run python:slim python --version
    Python 3.10.8
    $ ls
    __doc__  RustPython
    $ docker run -v $(pwd):/RustPython -w /RustPython/__doc__ python:slim python generate_docs.py ../RustPython docs.inc.rs


and do not forget to update cargo before the test
```
$ cargo update
```
## Why the `__doc__` is not changed?

### Check the old documentation implemented with remarks are still exist
RustPython prioritizes the user define documentation. Check if the old remarks are remaining in the source code. If it is, simply removing them could solve the issue.

## Contributing

Contributions are more than welcome, and in many cases we are happy to guide
contributors through PRs or on gitter. Please refer to the
[development guide](https://github.com/RustPython/RustPython/DEVELOPMENT.md) as well for tips on developments.

## License

This project is licensed under the MIT license. Please see the
[LICENSE](https://github.com/RustPython/RustPython/LICENSE) file for more details.

The [project logo](https://github.com/RustPython/RustPython/logo.png) is licensed under the CC-BY-4.0
license. Please see the [LICENSE-logo](https://github.com/RustPython/RustPython/LICENSE-logo) file
for more details.