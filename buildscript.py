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
parser.add_option("-o", type="string", dest="output_file_name")
parser.add_option("-t", type="string", dest="target", default="cuda")
parser.add_option("-m", type="int", dest="arch_size", default=64)

truncated_arg_list =  sys.argv[1:] # We don't want "python" and "buildscript.py" in our list
(options, args) = parser.parse_args(truncated_arg_list)

# use base_file_name if output file name is not specified
output_file_name = options.output_file_name
output_file_name = base_file_name if output_file_name is None else os.path.splitext(output_file_name)[0]

target = options.target
VALID_TARGETS = ["cl", "cuda"]
TARGET_FLAGS = {
            'cl': {
                32: 'nvptx--nvidiacl',
                64: 'nvptx64--nvidiacl'
                },
            'cuda': {
                32: 'nvptx--',
                64: 'nvptx64--'
            }
        }

arch_size = options.arch_size

if target not in VALID_TARGETS:
    print "WARNING!!: Your target is bogus" #TODO: throw an exception and bail out

target = TARGET_FLAGS[target][arch_size]

cl_file_name = "%s.cl" % base_file_name
ir_file_name = "%s.ll" % base_file_name
front_end_stage = "clang -Dcl_clang_storage_class_specifiers -I/home/chae14/llvm-ptx-samples/libclc/include/generic -I/home/chae14/llvm-ptx-samples/libclc/include/ptx -include clc/clc.h -target {0} {1} -emit-llvm -S -o {2}".format(target, cl_file_name, ir_file_name)
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
linker_stage = "llvm-link libclc/install/lib/clc/{0}.bc {1} -o {2}".format(target, ir_file_name, linked_file_name)
subprocess.call(linker_stage.split())

ptx_file_name = "%s.nvptx.s" % output_file_name
backend_stage = "clang -target {0} {1} -S -o {2}".format(target, linked_file_name, ptx_file_name)
subprocess.call(backend_stage.split())

ptx_run_stage = "ptxjit {0}".format(ptx_file_name)
subprocess.call(ptx_run_stage.split())
