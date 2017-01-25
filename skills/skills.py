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
f=open("add.c","w")
code = """double add(float a, float b) {
   return a+b;
   }
   
"""

extension_c_code = """

#include <Python.h>

static PyObject *
  Py_myadd(PyObject *self,PyObject *args)
{
  double a,b;
  if (!PyArg_ParseTuple(args,"ff",&a,&b))
    return NULL;
  return Py_BuildValue("f",add(a,b));
}

static PyMethodDef MyExtMethods[]= {
  {"add", Py_myadd , METH_VARARGS},
  {NULL, NULL} /*sentinel */
};
static struct PyModuleDef cmodule = {
   PyModuleDef_HEAD_INIT,
   "c",   /* name of module */
   NULL, /* module documentation, may be NULL */
   -1,       /* size of per-interpreter state of the module,
   or -1 if the module keeps state in global variables. */
   MyExtMethods
                               };
PyMODINIT_FUNC PyInit_c(void)
{
     PyObject *m;

     m = PyModule_Create(&cmodule);
     if (m == NULL)
         return NULL;
    return m;
}
"""
print(code+extension_c_code,file=f)
#print >>f, code+extension_c_code


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
print("BDIR:",build_dir)
sys.path.append(build_dir)
#import extend
import extend.c
print("DIR",dir(extend))