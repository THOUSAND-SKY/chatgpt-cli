def safe_get_element_by_index(lst, index):
    if index < 0 or index >= len(lst):
        return None
    return lst[index]
