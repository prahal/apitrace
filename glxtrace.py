##########################################################################
#
# Copyright 2008-2009 VMware, Inc.
# All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
##########################################################################/


from stdapi import *
from glapi import glapi
import trace


glxapi = API("GLX")

PROC = Opaque("__GLXextFuncPtr")

glxapi.add_functions(glapi.functions)
glxapi.add_functions([
    Function(PROC, "glXGetProcAddressARB", [(Alias("const GLubyte *", CString), "procName")]),
    Function(PROC, "glXGetProcAddress", [(Alias("const GLubyte *", CString), "procName")]),
])


class GlxTracer(trace.Tracer):

    def get_function_address(self, function):
        if function.name.startswith("glXGetProcAddress"):
            return 'dlsym(RTLD_NEXT, "%s")' % (function.name,)
        else:
            print '    if (!pglXGetProcAddress) {'
            print '        pglXGetProcAddress = (PglXGetProcAddress)dlsym(RTLD_NEXT, "glXGetProcAddress");'
            print '        if (!pglXGetProcAddress)'
            print '            Log::Abort();'
            print '    }'
            return 'pglXGetProcAddress((const GLubyte *)"%s")' % (function.name,)

    def wrap_ret(self, function, instance):
        if function.name.startswith("glXGetProcAddress"):
            print '    if (%s) {' % instance
            for f in glxapi.functions:
                ptype = self.function_pointer_type(f)
                pvalue = self.function_pointer_value(f)
                print '        if(!strcmp("%s", (const char *)procName)) {' % f.name
                print '            %s = (%s)%s;' % (pvalue, ptype, instance)
                print '            %s = (%s)&%s;' % (instance, function.type, f.name);
                print '        }'
            print '    }'


if __name__ == '__main__':
    print
    print '#include <stdlib.h>'
    print '#include <string.h>'
    print '#include <dlfcn.h>'
    print '#include <X11/Xlib.h>'
    print '#include <GL/gl.h>'
    print '#include <GL/glext.h>'
    print '#include <GL/glx.h>'
    print '#include <GL/glxext.h>'
    print
    print '#include "log.hpp"'
    print '#include "glhelpers.hpp"'
    print
    print 'extern "C" {'
    print
    tracer = GlxTracer()
    tracer.trace_api(glxapi)
    print
    print '} /* extern "C" */'