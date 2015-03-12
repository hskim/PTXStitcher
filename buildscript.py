#!/usr/bin/python
import sys
import subprocess
import os.path
from optparse import OptionParser


def compilation_path1(base_file_name):
    '''
    Using the compilation path suggested here
    http://renren.io/questions/484488/how-to-use-clang-to-compile-opencl-to-ptx-code
    '''
    cl_file_name = "%s.cl" % base_file_name
    ir_file_name = "%s.ll" % base_file_name
    front_end_stage = "clang -Dcl_clang_storage_class_specifiers -isystem libclc/install/include -include clc/clc.h -target nvptx64-- {0} -emit-llvm -S -o {1}".format(cl_file_name, ir_file_name)
    #front_end_stage = "clang -Dcl_clang_storage_class_specifiers -isystem libclc/install/include -isystem libclc/install/include/clc/workitem -include clc/clc.h -target nvptx64-- {0} -emit-llvm -S -o {1}".format(cl_file_name, ir_file_name)

    subprocess.call(front_end_stage.split())

    linked_file_name = "%s.linked.bc" % base_file_name
    #linker_stage = "llvm-link libclc/built_libs/nvptx64--.bc {0} -o {1}".format(ir_file_name, linked_file_name)
    linker_stage = "llvm-link libclc/install/lib/clc/nvptx64--nvidiacl.bc {0} -o {1}".format(ir_file_name, linked_file_name)
    subprocess.call(linker_stage.split())

    ptx_file_name = "%s.nvptx.s" % base_file_name
    backend_stage = "clang -target nvptx64 {0} -S -o {1}".format(linked_file_name, ptx_file_name)
    subprocess.call(backend_stage.split())

def compilation_path2(base_file_name):
    '''
    Using the compilation path in llvm-ptx-samples
    '''
    cl_file_name = "%s.cl" % base_file_name
    ir_file_name = "%s.ll" % base_file_name
    front_end_stage = "clang -Dcl_clang_storage_class_specifiers -I/home/chae14/llvm-ptx-samples/libclc/include/generic -I/home/chae14/llvm-ptx-samples/libclc/include/ptx -include clc/clc.h -target nvptx64 {0} -emit-llvm -S -o {1}".format(cl_file_name, ir_file_name)
    subprocess.call(front_end_stage.split())

    linked_file_name = "%s.linked.bc" % base_file_name
    linker_stage = "llvm-link libclc/install/lib/clc/nvptx64--.bc {0} -o {1}".format(ir_file_name, linked_file_name)
    subprocess.call(linker_stage.split())

    ptx_file_name = "%s.nvptx.s" % base_file_name
    backend_stage = "clang -target nvptx64-nvidia-nvcl {0} -S -o {1}".format(linked_file_name, ptx_file_name)
    subprocess.call(backend_stage.split())



def base_file_name(file_name):
    '''
    parse file name and append appropriate filename
    # test.cl --> test  so that it can be used to create test.ll or test.linked.bc
    '''
    base_name = os.path.basename(file_name)
    name_without_extension = os.path.splitext(base_name)[0]
    return name_without_extension

base_file_name = "test"

parser = OptionParser()
parser.add_option("--opt-flags", type="string", dest="opt_code_flags")
truncated_arg_list =  sys.argv[1:] # We don't want "python" and "buildscript.py" in our list
(options, args) = parser.parse_args(truncated_arg_list)


cl_file_name = "%s.cl" % base_file_name
ir_file_name = "%s.ll" % base_file_name
front_end_stage = "clang -Dcl_clang_storage_class_specifiers -I/home/chae14/llvm-ptx-samples/libclc/include/generic -I/home/chae14/llvm-ptx-samples/libclc/include/ptx -include clc/clc.h -target nvptx64 {0} -emit-llvm -S -o {1}".format(cl_file_name, ir_file_name)
subprocess.call(front_end_stage.split())

if options.opt_code_flags:
    opt_code_flags = options.opt_code_flags
    opt_code_flags_set = set(opt_code_flags.split())

    should_use_ll = "-S" in set(opt_code_flags.split())
    ir_file_extension = "ll" if should_use_ll else "bc"

    unoptimized_ir_file_name = ir_file_name
    optimized_ir_file_name = "{0}.opt.{1}".format(base_file_name, ir_file_extension)
    optimization_stage = "opt " + opt_code_flags + " {0} -o {1}".format(unoptimized_ir_file_name, optimized_ir_file_name)
    subprocess.call(optimization_stage.split())
    ir_file_name = optimized_ir_file_name

linked_file_name = "%s.linked.bc" % base_file_name
linker_stage = "llvm-link libclc/install/lib/clc/nvptx64--.bc {0} -o {1}".format(ir_file_name, linked_file_name)
subprocess.call(linker_stage.split())

ptx_file_name = "%s.nvptx.s" % base_file_name
backend_stage = "clang -target nvptx64-nvidia-nvcl {0} -S -o {1}".format(linked_file_name, ptx_file_name)
subprocess.call(backend_stage.split())
