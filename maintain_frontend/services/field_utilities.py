# additional testing required as one value could be None and the other ''. For our purposes they are the same.
def has_value_changed(value, new_value):
    if (not(value) and new_value):
        return True
    if value and value != new_value:
        return True
    return False


def get_ordered_edited_fields(edited_fields, review_map):
    result = []
    for mapping in review_map:
        if mapping.name in edited_fields:
            result.append(mapping.name)
    return result
