from urllib.parse import urlsplit, urlunsplit, parse_qs


def change_params_in_url(url: str, replace_dict: dict):
    """
    :param url: string url
    :param replace_dict: dictionary {param_name: new_value, param_name2: new_value2}
    :return: string url
    """
    split_url = urlsplit(url)
    query = split_url.query
    query_dict = parse_qs(query)

    for k, v in replace_dict.items():
        if k not in query_dict.keys():
            raise KeyError(f"{k}")
        query_dict[k] = [v]

    new_query = "?"
    for k, v in query_dict.items():
        if new_query != "?":
            new_query += "&"
        new_query += f"{k}={v[0]}"

    return urlunsplit(
        [
            split_url.scheme,
            split_url.netloc,
            split_url.path,
            new_query,
            split_url.fragment,
        ]
    )
