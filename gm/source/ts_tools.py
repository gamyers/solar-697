from itertools import product

def gen_arima_params(p_rng=(0, 0), d_rng=(0, 0), q_rng=(0, 0)):
    """
    input: 3 tuples of inclusive value ranges
    Primary function: produce a cartesian product of the inputs 
    output: list of 3-tuple products
    """
    p = range(p_rng[0], p_rng[1]+1)
    d = range(d_rng[0], d_rng[1]+1)
    q = range(q_rng[0], q_rng[1]+1)

    # Create a list with all possible combination of parameters
    parameters = product(p, d, q)
    parameters_list = list(parameters)

    order_list = []

    for each in parameters_list:
        each = list(each)
        # each.insert(1, 1)
        each = tuple(each)
        order_list.append(each)

    print(f"Order list length: {len(order_list)}")
    # order_list[:10]
    
    return order_list