#!/usr/bin/python
import sys
import subprocess
import os.path
from optparse import OptionParser
from ConfigParser import ConfigParser


def base_file_name(file_name):
    '''
    parse file name and append appropriate filename
    # test.cl --> test  so that it can be used to create test.ll or test.linked.bc
    '''
    base_name = os.path.basename(file_name)
    name_without_extension = os.path.splitext(base_name)[0]
    return name_without_extension

configuration = ConfigParser()
configuration.read("config.cfg")
libclc_path = configuration.get('Environment', 'libclc_path')

if type(libclc_path) is 'str' and libclc_path[0] in ['\"', '\'']:
    print "WARNING: libclc_path is string but config.cfg does not expect the value to be wrapped around in single or double quotes"

parser = OptionParser()
parser.add_option("--opt-flags", type="string", dest="opt_code_flags", 
        help="Flags that will be passed to 'opt' phase. Flags should be passed as if they are being passed directly to opt. For example --opt-flags=\'-flag1 -flag2 -flag3\'")
parser.add_option("-o", type="string", dest="output_file_name",
        help="Name of the output file. By default, it will use the base name of the input. For example, if input file was \'helloworld.cl\', and no output name was specified, output will be \'helloworld.nvptx.s\'")
parser.add_option("-t", type="string", dest="target", default="cuda",
        help="Specify target. Valid targets: [cuda, cl]. Default: cuda")
parser.add_option("-m", type="int", dest="arch_size", default=64,
        help="Specify architecture size. Valid sizes: [32, 64]. Default: 64")

truncated_arg_list =  sys.argv[1:] # We don't want "python" and "cl2ptx.py" in our list
(options, args) = parser.parse_args(truncated_arg_list)

base_file_name = base_file_name(truncated_arg_list[-1])

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
front_end_stage = "clang -Dcl_clang_storage_class_specifiers -I{0}/include/generic -I{0}/include/ptx -include clc/clc.h -target {1} {2} -emit-llvm -S -o {3}".format(libclc_path, target, cl_file_name, ir_file_name)
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
linker_stage = "llvm-link {0}/install/lib/clc/{1}.bc {2} -o {3}".format(libclc_path, target, ir_file_name, linked_file_name)
subprocess.call(linker_stage.split())

ptx_file_name = "%s.nvptx.s" % output_file_name
backend_stage = "clang -target {0} {1} -S -o {2}".format(target, linked_file_name, ptx_file_name)
subprocess.call(backend_stage.split())

ptx_run_stage = "ptxjit {0}".format(ptx_file_name)
subprocess.call(ptx_run_stage.split())
