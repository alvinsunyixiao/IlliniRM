import math

def contour_with_n_contour_inside(hierarchy_list, desired_number):
    processed_id_marker = []
    max_number = 0
    for n, i in enumerate(hierarchy_list):
        if n in processed_id_marker: continue
        no_of_siblings = sibling_counter(hierarchy_list, n, action = "init", marker = None)
        if no_of_siblings >= desired_number: return i[3]
        if no_of_siblings > max_number: max_number = no_of_siblings
        processed_id_marker.append(n)
    print "Failed to find specified target. Max number: ", str(no_of_siblings)
    return None

def sibling_counter(hierarchy_list, desired_node_id, action = "init", marker = None):
    if desired_node_id == -1: return 0
    desired_node = hierarchy_list[desired_node_id]
    if desired_node[3] == -1: return 0 #root node does not count
    next_node_id = desired_node[0]
    previous_node_id = desired_node[1]
    if marker: marker.append(desired_node_id)
    if action == "init":
        return sibling_counter(hierarchy_list, next_node_id, action = "forward", marker = marker) + sibling_counter(hierarchy_list, previous_node_id, action = "backward", marker = marker) + 1
    if action == "forward":
        return sibling_counter(hierarchy_list, next_node_id, action = "forward", marker = marker) + 1
    if action == "backward":
        return sibling_counter(hierarchy_list, previous_node_id, action = "backward", marker = marker) + 1
