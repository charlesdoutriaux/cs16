## ref for py3 extensions: http://python3porting.com/cextensions.html
from distutils.core import setup, Extension
import os
import sys
import glob
## Becuse we can only have one .txt file all extensions
## Have to be written from within this file
## same for the setup.py file

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
with open("add.c","w") as f:
    print(code+extension_c_code,file=f)
    #print >>f, code+extension_c_code

init_src = """# __init__ """
with open("__init__.py","w") as f:
    print(init_src,file=f)
    #print >>f,init_src



setup (name = "extend",
       version='1.0',
       author='Charles Doutriaux',
       description = "Python Interface to C",
       packages = ['extend'],
       package_dir = {'extend': '.'},
       ext_modules = [
    Extension('extend.c',
              ["add.c"],
	      #include_dirs = include_dirs,
              #library_dirs = library_dirs,
              #libraries = libraries,
              #define_macros = macros,
              #extra_compile_args = [ "@DEBUG@", ]
              ),
    
    ]
      )


build_dir = glob.glob(os.path.join("build","*"))[0]
sys.path.append(build_dir)
import extend
import extend.c

class Add(object):
    __slots__ = [
            "_language",
            ]
    def __init__(self,language="python"):
        self.language=language
    @property
    def language(self):
        return self._language
    @language.setter
    def language(self,value):
        if not isinstance(value,str):
            raise ValueError("language must be a string")
        elif not value.lower() in ["c","python"]:
            raise ValueError("%s not implemented yet")
        self._language = value.lower()

    def add(self,a,b):
        if self.language == "c":
            return extend.c.add(float(a),float(b))
        else:
            return float(a)+float(b)

# some basic tests
P = Add()
C = Add("C")



# Some timing for fun
import random
import time

def timeit(Operator,N=1000000):
    start = time.clock()
    for i in range(N):
        a = Operator.add(random.random(),random.random())
    end = time.clock()
    print("Using %s it took %f seconds to add %i times" % (Operator.language,end-start,N))

timeit(P)
timeit(C)


import unittest

class TestCase(unittest.TestCase):
    def test(self):
        self.assertTrue(P.add(2,3) == 5)
    def test2(self):
        print(C.add(2,3))
        self.assertTrue(C.add(2,3) == 5.)
    def test3(self):
        with self.assertRaises(AttributeError):
            P.bad = 5
    def test4(self):
        with self.assertRaises(ValueError):
            P.language = "Fortran"
    def test5(self):
        P.language = "c"
        self.assertTrue(P.language == "c")
        P.language = "python"
sys.argv[1:]=[]
unittest.main()
