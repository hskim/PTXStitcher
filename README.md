PTXStitcher
====================

## Dependencies ##

* libclc
* clang 3.4 >=
* llvm
* gcc4.8
* ptxjit
Note: Please refer to this [link](http://tiku.io/questions/484488/how-to-use-clang-to-compile-opencl-to-ptx-code) to configure libclc and clang with ptx support.

## Setup ##
1. Run `chmod +x cl2ptx.py` to make the python script executable
2. Add the path to `cl2ptx.py` to `PATH`.
3. Edit `config.cfg` with proper configuration.

## Usage ##
To check out available flags, run `./cl2ptx.py --help`.

## How It Works ##
Internally it calls series of clang tools which you would have to call yourself otherwise.

1. cl --> ll
```clang -Dcl_clang_storage_class_specifiers -Ipath/to/include/generic -Ipath/to/include/ptx -include clc/clc.h -target target-passed-in-as-flag foo.cl -emit-llvm -S foo.ll```
2. ll --> ll or bc (optional ```opt``` stage, if you decide to add optimization stage)
```opt passed-in-opt-flags foo.ll -o foo.opt.ll```
3. ll or bc --> linked.bc (linking stage)
```llvm-link path/to/install/lib/clc/target-library.bc foo.ll -o foo.linked.bc```
4. linked.bc --> nvptx.s (final backend)
```clang -target target-passed-in-as-flag foo.linked.bc -S -o foo.nvptx.s```
