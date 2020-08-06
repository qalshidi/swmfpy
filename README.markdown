![swmfpy logo](share/logo/swmfpy.png "swmfpy")

swmfpy
======

A collection of tools to make it easier to work with Python and Space Weather Modeling Framework (SWMF) together.

This is a work in progress.

Installation
------------

*Note*: swmfpy also is part of the SWMF and gets cloned into `SWMF/share/Python`. However, if you would like to [develop](CONTRIBUTING.markdown) for swmfpy make a clone and work that way and make a merge request.

There are two methods of installing swmfpy with with a virtual environment and without a virtual environment. Only use the virtual environment if your current environment is giving you trouble.

### Without Python venv

Install with [pip](https://pip.pypa.io/en/stable/):

```shell
$ python3 -m pip install --user wheel  # Might be necessary
$ python3 -m pip install --user git+https://gitlab.umich.edu/swmf_software/swmfpy.git@master
```

*Note*: Depending on your system [pip](https://pip.pypa.io/en/stable/) may be ran in other ways: `python3 -m pip` or `python -m pip`

Then import it into your python project. 

```python
import swmfpy
```

### With Python venv

Use this method if the above method is giving you trouble.

Set up a python 3 virtual environment:

```bash
$ python3 -m venv ~/.venv
```

This is important, make sure that it is in your `.profile` or `.bash_profile`:

```bash
$ echo "source ~/.venv/bin/activate" >> ~/.profile
```

*Note*: You might need to use `activate.csh` instead if using `csh` and `activate.fish` in your `~/.config/fish/config.fish` instead if using `fish` shell. You are most likely using `bash` so no need to worry.

Next install the software. This will take a long time as you will be compiling `numpy` from scratch.

```bash
$ source ~/.venv/bin/activate
$ python3 -m pip install --user wheel -vvv
$ python3 -m pip install --user cython -vvv
$ python3 -m pip install --user git+https://gitlab.umich.edu/swmf_software/swmfpy.git@master
```

If you are using `tmux` or `GNU Screen` on a supercomputer you can safely detach your session and power off your computer and come back another time.

This should be fully installed now. You should be able to import:

```python
import swmfpy
```

### Troubleshooting

If you have followed these carefully and still not been able to install please submit an Issue.

Documentation
-------------

An auto-documented version can be found [here](DOCUMENTATION.markdown).

However, documentation is included as docstrings. Use python's *dir()* and *help()* inbuilt functions to see documentation.

```python
import swmfpy
help(swmfpy)  # To see list of functions
help(swmfpy.io.read_gm_log)  # To see the function documentation
```

Issues
------

If you are experiencing any issues or bugs please go to the [Issues](https://gitlab.umich.edu/swmf_software/swmfpy/issues) page and create an issue. Make sure you include steps to recreate the problem in your post.

How to cite
-----------

You can cite this software on LaTeX like this:

```latex
@software{swmfpy,
  author = {{Al Shidi, Qusai}},
  title = {swmfpy},
  url = {https://gitlab.umich.edu/swmf_software/swmfpy},
  version = {2020.5},
  date = {2020-06-19},
}
```
