class MyException(Exception):
    pass

# args is args list
# target is string to search for in args list
# if target in args list, return the value set in args
# otherwise return the default value
def set_param_int(args, target, default_value):
    if not target in args:
        return default_value
    try:
        return int(args[args.index(target) + 1])
    except:
        raise MyException('Failed to cast in in parameters. ' +
            'This argument requires an int and you did not provide one ..')

def set_param_gen(args, target, default_value):
    if not target in args:
        return default_value
    return args[args.index(target) + 1]

# args is the args list
# target is string to search for in args list
# if target in list, return True, else False
def set_param_bool(args, target):
    return target in args
