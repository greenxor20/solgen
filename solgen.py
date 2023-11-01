#!/bin/python

import json
import sys, os, stat

NO_DEFAULT_VAL = "__NO_DEFAULT_VAL__"

def extract_arg_decl(name: str, dtype: str, default: str = NO_DEFAULT_VAL):
    res = f"{name}: {dtype}"
    if default != NO_DEFAULT_VAL:
        res += f" = {default}"
    return res

def combine_with_comma(ls: list)->str:
    res = ""
    for s in ls:
        res += s + ", "
    if len(ls) > 0:
        res = res[:-2]
    return res

def get_name_dtype_list_str(args: list)->str:
    res = []
    for arg in args:
        res.append(f"""('{arg["name"]}', '{arg["dtype"]}')""")
        
    return f"[{combine_with_comma(res)}]"

def extract_arg_invokation(idx: int, dtype: str):
    return f"{dtype}(args[{idx}])"

if __name__ == "__main__":
    jsfile_name = None
    if len(sys.argv) >= 2:
        jsfile_name = sys.argv[1]
    else:
        jsfile_name = input("enter name of json file: ")
    
    assert(jsfile_name.endswith(".json"))
        
    
    inf = open(jsfile_name, 'r')
    conf = json.load(inf)
    print(f"running on conf:\n{json.dumps(conf, indent=2)}")
    
    func_name = conf["name"]
    args = conf["args"]
    
    #translate shorthands:
    args = [{"name": arg} if type(arg) is str else arg for arg in args]
    args = [arg if "dtype" in arg.keys() else {**arg, "dtype": "str"} for arg in args]
    
    #find and check default arg indices:
    first_default_arg_idx = None
    last_default_arg_idx = None
    for idx, arg in enumerate(args):
        if "default" in arg.keys():
            if first_default_arg_idx is None:
                first_default_arg_idx = idx
            last_default_arg_idx = idx
    if first_default_arg_idx is None:
        first_default_arg_idx = len(args)
    
    assert(last_default_arg_idx is None or last_default_arg_idx == len(args)-1)
    
    #func body string
    func_body = conf["body"] if "body" in conf.keys() else "pass"
    
    #typelist def string
    typelist_def = f"""typelist = [{combine_with_comma([arg["dtype"] for arg in args])}]"""
    
    #invokation args string
    invokation_args = f"""*[typelist[idx](arg) for (idx, arg) in enumerate(args)]"""
    
    
    #invokation_args = f"""{combine_with_comma([extract_arg_invokation(idx, arg["dtype"]) for (idx, arg) in enumerate(args)])}"""
    
    #arg assignment string
    arg_assignment = f"""args = None
    if len(argv) < {first_default_arg_idx+1}:
        print("not enough command line args. getting args from stdin...")
        args = [input(f"enter '{{name}}' ({{dtype}}): ") for (name, dtype) in {get_name_dtype_list_str(args)}]
    else:
        print("getting args from command line...")
        args = argv[1:]\
"""
    
    
    #decleration strings:
    decl_args_ls = [extract_arg_decl(**arg) for arg in args]
    decl_args_str = combine_with_comma(decl_args_ls)
    
    # create output file:
    outfile_name = jsfile_name.split(".")[0]+".py"
    print(f"printing res to file named '{outfile_name}'")
    
    outf = open(outfile_name, 'w')

    res = f"""#!/bin/python
import sys    

def {func_name}({decl_args_str}):
    {func_body}

def main(argv):
    {arg_assignment}
    {typelist_def}
    result = {func_name}({invokation_args})
    print(f"{{result=}}")

if __name__ == "__main__":
    main(sys.argv)
  
"""
    print(f"generated result:\n{res}")
    outf.write(res)
    outf.close()
    os.system(f"chmod +x {outfile_name}")

    
