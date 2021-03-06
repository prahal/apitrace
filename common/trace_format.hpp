/**************************************************************************
 *
 * Copyright 2010 VMware, Inc.
 * All Rights Reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 **************************************************************************/

/*
 * Trace binary format.
 *
 * Grammar:
 *
 *   trace = event* EOF
 *
 *   event = EVENT_ENTER call_sig call_detail+
 *         | EVENT_LEAVE call_no call_detail+
 *
 *   call_sig = sig_id ( name arg_names )?
 *
 *   call_detail = ARG index value
 *               | RET value
 *               | END
 *
 *   value = NULL
 *         | FALSE
 *         | TRUE
 *         | SINT int
 *         | UINT int
 *         | FLOAT float
 *         | DOUBLE double
 *         | STRING string
 *         | BLOB string
 *         | ENUM enum_sig
 *         | BITMASK bitmask_sig value
 *         | ARRAY length value+
 *         | STRUCT struct_sig value+
 *         | OPAQUE int
 *
 *   call_sig = id name arg_name*
 *            | id
 *
 *   enum_sig = id name value
 *            | id
 *
 *   bitmask_sig = id count (name value)+
 *               | id
 *
 *   string = length (BYTE)*
 *
 */

#ifndef _TRACE_FORMAT_HPP_
#define _TRACE_FORMAT_HPP_

namespace trace {

/*
 * Trace file version number.
 *
 * We keep backwards compatability reading old traces, i.e., it should always be
 * possible to parse and retrace old trace files.
 *
 * So the trace version number refers not only to changes in the binary format
 * representation, but also semantic changes in the way certain functions
 * should be retraced.
 *
 * Writing/editing old traces will not be supported however.  An older version
 * of apitrace should be used in such circunstances.
 *
 * Changelog:
 *
 * - version 0:
 *   - initial implementation
 *
 * - version 1:
 *   - support for GL user arrays -- a blob is provided whenever an user memory
 *   is referred (whereas before calls that operate wit user memory instead of
 *   VBOs should be ignore)
 *
 * - version 2:
 *   - malloc/free memory calls -- allow to pass user memory as malloc memory
 *   as opposed to blobs
 *   - glFlushMappedBufferRange will emit a memcpy only for the flushed range
 *   (whereas previously it would emit a memcpy for the whole mapped range)
 */
#define TRACE_VERSION 2

enum Event {
    EVENT_ENTER = 0,
    EVENT_LEAVE,
};

enum CallDetail {
    CALL_END = 0,
    CALL_ARG,
    CALL_RET,
    CALL_THREAD,
};

enum Type {
    TYPE_NULL = 0,
    TYPE_FALSE,
    TYPE_TRUE,
    TYPE_SINT,
    TYPE_UINT,
    TYPE_FLOAT,
    TYPE_DOUBLE,
    TYPE_STRING, // Null terminated, human readible string
    TYPE_BLOB, // Block of bytes
    TYPE_ENUM,
    TYPE_BITMASK,
    TYPE_ARRAY,
    TYPE_STRUCT,
    TYPE_OPAQUE,
};


} /* namespace trace */

#endif /* _TRACE_FORMAT_HPP_ */
