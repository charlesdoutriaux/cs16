# ref for py3 extensions: http://python3porting.com/cextensions.html
# This code is a sample code for:
#  - write C extension compatible for both python 3 and 2
#  - use classes
#  - use class properties
#  - use decorators
#  - write tests

# Things we could add to make this fancier
#  - ask user to pint to C file with function and functions names to wrap
#  - use argparse to process user inputs

import sys
from distutils.core import setup, Extension
import os
import glob
import unittest
import random
import time

# Because we can only have one .txt file all extensions
# Have to be written from within this file
# same for the setup.py file
# setup.py needs argument "build"
if sys.argv[-1] != "build":
    sys.argv.append("build")

# C extension code
code = """
double add(float a, float b) {
   return a+b;
   }

"""

extension_c_code = """

#include <Python.h>

static PyObject *
  Py_myadd(PyObject *self,PyObject *args)
{
  double a,b;
  if (!PyArg_ParseTuple(args,"dd",&a,&b))
    return NULL;
  return Py_BuildValue("f",add(a,b));
}

static PyMethodDef MyExtMethods[]= {
  {"add", Py_myadd , METH_VARARGS},
  {NULL, NULL} /*sentinel */
};
#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit_c(void)
  {
    static struct PyModuleDef cmodule = {
       PyModuleDef_HEAD_INIT,
       "c",   /* name of module */
       NULL, /* module documentation, may be NULL */
       -1,       /* size of per-interpreter state of the module,
       or -1 if the module keeps state in global variables. */
       MyExtMethods,
       NULL,
       NULL,
       NULL,
       NULL
    };
PyObject *m;
m = PyModule_Create(&cmodule);
if (m == NULL)
    return NULL;

//if (PyModule_AddObject(m, "hookable", (PyObject *)&hookabletype) < 0)
//   return NULL;

return m;

};
#else
   PyMODINIT_FUNC initc(void){
       Py_InitModule3("c",MyExtMethods,NULL);
   };
#endif

"""

# Create the files
with open("add.c", "w") as f:
    f.write(code + extension_c_code)

init_src = """# __init__ """
with open("__init__.py", "w") as f:
    f.write(init_src)

# Run setup to generate module locally
setup(name="extend",
      version='1.0',
      author='Charles Doutriaux',
      description="Python Interface to C",
      packages=['extend'],
      package_dir={'extend': '.'},
      ext_modules=[
           Extension('extend.c',
                     ["add.c"],
                     # include_dirs = include_dirs,
                     # library_dirs = library_dirs,
                     # libraries = libraries,
                     # define_macros = macros,
                     # extra_compile_args = [ ]
                     ),

      ]
      )


# Add build directory to path so we can import
build_dir = glob.glob(os.path.join("build", "*"))[0]
sys.path.append(build_dir)
import extend  # noqa
import extend.c  # noqa


# Create class to route the function to the proper language implementation
class Add(object):
    # reserved slots
    __slots__ = [
        "_language",
    ]

    # initialize class
    def __init__(self, language="python"):
        self.language = language

    # getting the language, nothing fancy
    @property
    def language(self):
        return self._language

    # Some basic checks when setting the language
    @language.setter
    def language(self, value):
        if not isinstance(value, str):
            raise ValueError("language must be a string")
        elif not value.lower() in ["c", "python"]:
            raise ValueError("%s not implemented yet")
        self._language = value.lower()

    # The routing function
    def add(self, a, b):
        if self.language == "c":
            return extend.c.add(float(a), float(b))
        else:
            return float(a) + float(b)


# Some timing for fun
def timeit(Operator, N=1000000):
    """Runs function 'add' N times on Operator and time it """
    # Record start time
    start = time.clock()
    for i in range(N):  # loop N times
        Operator.add(random.random(), random.random())
    end = time.clock()
    print("Using %s it took %f seconds to add %i times" %
          (Operator.language, end - start, N))


# Default language is Python
P = Add()
# Create a C-based one
C = Add("C")
# run the timing test for both
timeit(P)
timeit(C)

# Unittestit, have to put it last because it exits
class TestCase(unittest.TestCase):

    def test(self):
        """validate result Python"""
        P = Add()
        self.assertTrue(P.add(2, 3) == 5)

    def test2(self):
        """Validate C result"""
        C = Add("C")
        self.assertTrue(C.add(2, 3) == 5.)

    def test3(self):
        """Validate you cannot set anything not 'language'"""
        with self.assertRaises(AttributeError):
            P.bad = 5

    def test4(self):
        """Validates you cannot pass unsupported language"""
        with self.assertRaises(ValueError):
            P.language = "Fortran"

    def test5(self):
        """Validates language changes"""
        P = Add()
        P.language = "c"
        self.assertTrue(P.language == "c")
        P.language = "python"


sys.argv[1:] = []
unittest.main()
