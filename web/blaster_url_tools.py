from urllib.parse import urlsplit, urlunsplit, parse_qs, urlencode


def change_params_in_url(url: str, replace_dict: dict, strict=True):
    """
    :param url: string url
    :param replace_dict: dictionary {param_name: new_value, param_name2: new_value2}
    :param strict: if True (default) will only replace existing params, if False will add new params to URL
    :return: string url
    """
    split_url = urlsplit(url)
    query = split_url.query
    query_dict = parse_qs(query)

    for k, v in replace_dict.items():
        if strict and k not in query_dict.keys():
            raise KeyError(f"{k}")
        query_dict[k] = [v]

    new_query = urlencode(query_dict)

    return urlunsplit(
        [
            split_url.scheme,
            split_url.netloc,
            split_url.path,
            new_query,
            split_url.fragment,
        ]
    )
