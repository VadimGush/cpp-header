# C++ one header builder

Simple Python script that builds one header for your C++ library. All you need is to provide path to your source files.

## Execution

Just run the script and redirect the output to a new file. The only argument is the path to your source files.
Script will scan content of that directory and it will combine all header files into one.
```bash
./header.py <path_to_src> > lib.h
```

You can also specify path to the file with license which will be included at the begging of header file:
```bash
./header.py --license <licence_file> <path_to_src> > lib.h
```

## Motivation
Because why not.
