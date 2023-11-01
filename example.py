
import sys    

def foo(arg1: bool, arg2: str, arg4: str, arg3: int):
    print(arg1, arg2, arg3)

def main(argv):
    args = None
    if len(argv) < 5:
        print("not enough command line args. getting args from stdin...")
        args = [input(f"enter '{name}' ({dtype}): ") for (name, dtype) in [('arg1', 'bool'), ('arg2', 'str'), ('arg4', 'str'), ('arg3', 'int')]]
    else:
        print("getting args from command line...")
        args = argv[1:]
    foo(bool(args[0]), str(args[1]), str(args[2]), int(args[3]))

if __name__ == "__main__":
    main(sys.argv)
  
