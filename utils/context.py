
def parse_context(data_items):
    """
    Parses a list of data items and extracts their content fields.

    Args:
        data_items (list): A list of dictionaries, each representing a data item with a 'content' field.

    Returns:
        str: A string containing each content field on a new line.
    """
    # Extract the 'content' field from each data item and join them with newlines
    parsed_context = "\n".join(item.get("content", "") for item in data_items if item.get("content"))
    return parsed_context