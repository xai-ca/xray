import pathlib
from collections import defaultdict
import clingo
import re

from py_arg_visualisation.functions.graph_data_functions.get_color import get_color

PATH_TO_ENCODINGS = pathlib.Path(__file__).parent / "encodings"


def generate_plain_dot_string(argumentation_framework, layout=any, raw_json=any):
    dot_string = "digraph {\n "
    dot_string += 'rankdir={}  \n \n node [fontname = "helvetica" , shape=circle, fixedsize=true, width=0.8, height=0.8] \n '.format(
        layout
    )
    arg_meta = {n["id"]: n for n in raw_json.get("arguments", [])}

    # Adding node information
    for arg in argumentation_framework.arguments:
        name = arg.name
        meta = arg_meta.get(name, {})
        attrs = [f'label="{name}"', "fontsize=14",'target="_blank"']
        if meta.get("annotation"):
            # tooltip shows on hover in many viewers
            tip = meta["annotation"].replace('"', '\\"')
            attrs.append(f'tooltip="{tip}"')
        if meta.get("url"):
            attrs.append(f'URL="{meta["url"]}"')
        dot_string += (f'  "{name}" [{", ".join(attrs)}]\n')

    # Adding edge information
    dot_string += '\n edge[labeldistance=1.5 fontsize=12 fontname="helvetica"]\n'
    for attack in argumentation_framework.defeats:
        dot_string += f'    "{attack.from_argument}" -> "{attack.to_argument}"\n'
    dot_string += "}"

    return dot_string


def extract_node_positions(layout_file):
    """
    Reads a layout.txt file and extracts node positions.

    Args:
        layout_file (str): Path to the layout file.

    Returns:
        dict: A dictionary mapping node names to (x, y) positions.
    """
    node_positions = {}

    try:
        with open(layout_file, "r") as f:
            lines = f.readlines()

        for line in lines:
            parts = line.split()
            if parts and parts[0] == "node":
                node_id = parts[1]  # Node name
                x, y = float(parts[2]), float(parts[3])  # Extract x, y coordinates
                node_positions[node_id] = (x, y)

    except FileNotFoundError:
        print(f"Warning: Layout file {layout_file} not found. Using default positions.")
    except Exception as e:
        print(f"Error reading layout file {layout_file}: {e}")

    return node_positions


def generate_dot_string(
    argumentation_framework,
    selected_arguments,
    color_blind_mode=False,
    layout=any,
    rank=any,
    special_handling=any,
    layout_freeze=False,
    layout_file=None,
    raw_json=None,
):
    # print(raw_json)
    arg_meta = {n["id"]: n for n in raw_json.get("arguments", [])} if raw_json else {}
    gr_status_by_arg, number_by_argument = get_numbered_grounded_extension(
        argumentation_framework
    )
    # processing the layout file
    layout_file = (
        pathlib.Path(__file__).parent.parent.parent.parent.parent
        / "temp"
        / "layout.txt"
    )
    node_positions = extract_node_positions(layout_file) if layout_file else {}
    # print(node_positions)

    if layout_freeze:
        graph_layout = "graph[layout=neato overlap=false]"
    else:
        graph_layout = "layout=dot"

    # creating the dot string
    dot_string = f"digraph {{\n{graph_layout} \n"
    dot_string += 'rankdir={} \n \n node [fontname = "helvetica"  shape=circle fixedsize=true width=0.8, height=0.8] \n'.format(
        layout
    )

    # Adding node information
    is_extension_representation = False
    argument_extension_state = {}
    unselected_arguments = {arg.name for arg in argumentation_framework.arguments}
    for color, arguments in selected_arguments.items():
        if color in ["green", "red", "yellow"]:
            is_extension_representation = True
        if color == "green":
            status = "accepted"
        elif color == "red":
            status = "defeated"
        elif color == "yellow":
            status = "undefined"
        else:
            status = "other"
        for argument_name in arguments:
            if argument_name != "":
                number = number_by_argument[argument_name]
                argument_extension_state[argument_name] = status
                if gr_status_by_arg[argument_name] == "undefined" and status in [
                    "accepted",
                    "defeated",
                ]:
                    argument_color = get_color(f"light-{color}", color_blind_mode)
                else:
                    argument_color = get_color(color, color_blind_mode)
                if is_extension_representation:
                    argument_label = f"{argument_name}.{number}"
                else:
                    argument_label = argument_name

                pos_attr = (
                    f'pos="{node_positions[argument_name][0]},{node_positions[argument_name][1]}!"'
                    if argument_name in node_positions and layout_freeze
                    else ""
                )
                meta = arg_meta.get(argument_name, {})
                tip = meta.get("annotation", "").replace('"', '\\"')
                url = meta.get("url", "")
                
                node = (
                    f'    "{argument_name}" [style="filled" '
                    f'fillcolor="{argument_color}" '
                    f'label="{argument_label}" '
                    f'fontsize=14 {pos_attr}'
                )
                
                if tip:
                    node += f' tooltip="{tip}"'
                if url:
                    node += f' URL="{url}" target="_blank"'
                
                node += "]\n"
                dot_string += node

                unselected_arguments.remove(argument_name)
    for argument_name in unselected_arguments:
        dot_string += f'    "{argument_name}" [fontsize=14]\n'

    # Adding edge information
    dot_string += '\n edge[labeldistance=1.5 fontsize=12 fontname="helvetica"]\n'
    for attack in argumentation_framework.defeats:
        if is_extension_representation:
            from_argument_grounded_state = gr_status_by_arg[attack.from_argument.name]
            to_argument_grounded_state = gr_status_by_arg[attack.to_argument.name]
            from_argument_extension_state = argument_extension_state[
                attack.from_argument.name
            ]
            to_argument_extension_state = argument_extension_state[
                attack.to_argument.name
            ]
            from_argument_number = number_by_argument[attack.from_argument.name]
            to_argument_number = number_by_argument[attack.to_argument.name]

            # cal the against wind
            against_wind = False
            from_num = (
                float("inf")
                if from_argument_number == "∞"
                else int(from_argument_number)
            )
            to_num = (
                float("inf") if to_argument_number == "∞" else int(to_argument_number)
            )
            against_wind = from_num == float("inf") and to_num != float("inf")
            against_wind = against_wind or (from_num > to_num)

            if from_num == float("inf"):
                label = "∞"
            else:
                label = str(from_num + 1)

            # set initial style
            style = "solid"
            arrow_style = "vee"
            constraint_value = ""
            full_color = get_color("black", color_blind_mode)
            # handle grounded extensions
            # Accepted -> Defeated
            if (
                from_argument_grounded_state == "accepted"
                and to_argument_grounded_state == "defeated"
            ):
                full_color = get_color("edge-green", color_blind_mode)
            # Defeated -> Accepted
            elif (
                from_argument_grounded_state == "defeated"
                and to_argument_grounded_state == "accepted"
            ):
                full_color = get_color("edge-red", color_blind_mode)
            else:
                # handle the stable extensions
                # Stable Accepted -> Defeated (Grounded Undefined)
                if (
                    from_argument_extension_state == "accepted"
                    and to_argument_extension_state == "defeated"
                ):
                    extension_edge_color = get_color("edge-green", color_blind_mode)
                    full_color = f"{extension_edge_color}"
                    label = ""
                # Stable Defeated -> Accepted(Grounded Undefined)
                elif (
                    from_argument_extension_state == "defeated"
                    and to_argument_extension_state == "accepted"
                ):
                    extension_edge_color = get_color("edge-red", color_blind_mode)
                    full_color = f"{extension_edge_color}"
                    label = ""
                # Undefined -> Undefined
                elif (
                    from_argument_extension_state == "undefined"
                    and to_argument_extension_state == "undefined"
                ):
                    full_color = get_color("dark-yellow", color_blind_mode)
                # Undefined -> Defeated
                elif (
                    from_argument_extension_state == "undefined"
                    and to_argument_extension_state == "defeated"
                ):
                    full_color = get_color("gray", color_blind_mode)
                    style = "dotted"
                    arrow_style = "onormal"
                    constraint_value = set_constraint_con(special_handling, "BU")
                    label = ""
                # Defeated -> Undefined
                elif (
                    from_argument_extension_state == "defeated"
                    and to_argument_extension_state == "undefined"
                ):
                    full_color = get_color("gray", color_blind_mode)
                    style = "dotted"
                    arrow_style = "onormal"
                    constraint_value = set_constraint_con(special_handling, "BU")
                    label = ""
                # Defeated -> Defeated
                elif (
                    from_argument_extension_state == "defeated"
                    and from_argument_extension_state == "defeated"
                ):
                    full_color = get_color("gray", color_blind_mode)
                    style = "dotted"
                    arrow_style = "onormal"
                    constraint_value = set_constraint_con(special_handling, "BU")
                    label = ""

            if against_wind:
                if style == "dotted":
                    pass
                elif style == "invis":
                    pass
                else:
                    style = "dashed"
                constraint_value = set_constraint_con(special_handling, "RD")
                edge = (
                    f'"{attack.to_argument.name}" -> '
                    f'"{attack.from_argument.name}" '
                    f"[dir=back "
                    f'color="{full_color}" '
                    f'style= "{style}"'
                    f"{constraint_value}"
                    f'fontcolor="{full_color}"'
                    f'arrowtail="{arrow_style}"'
                    f'arrowhead="{arrow_style}"'
                    f'headlabel="{label}"]\n'
                )
            else:
                edge = (
                    f'"{attack.from_argument.name}" -> '
                    f'"{attack.to_argument.name}" '
                    f'[color="{full_color}" '
                    f'style="{style}"'
                    f"{constraint_value}"
                    f'fontcolor="{full_color}"'
                    f'arrowtail="{arrow_style}"'
                    f'arrowhead="{arrow_style}"'
                    f'taillabel="{label}"]\n'
                )
        else:
            edge = f'"{attack.from_argument.name}" -> "{attack.to_argument.name}"\n'
        dot_string += "    " + edge

    dot_string += "\n"
    # Enable Ranks
    number_by_argument = {k: v for k, v in number_by_argument.items() if v != "∞"}
    if rank == "NR":
        pass
    elif rank == "AR":
        # in case we need the rank = max
        # max_value = max(number_by_argument.values())
        filtered_arguments = {k: v for k, v in number_by_argument.items()}
        nodes_by_value = defaultdict(list)
        for node, value in filtered_arguments.items():
            nodes_by_value[value].append(node)
        for value in sorted(nodes_by_value.keys()):
            nodes = nodes_by_value[value]
            if len(nodes) == 1:
                same_rank_string = f"// {{rank = same {' '.join(nodes)}}}"
            else:
                same_rank_string = f"{{rank = same {' '.join(nodes)}}}"
            dot_string += f"    {same_rank_string}\n"
    elif rank == "MR":
        min_state_nodes = [
            node
            for node, value in number_by_argument.items()
            if value == min(number_by_argument.values())
        ]
        min_rank_string = f"{{rank = min {' '.join(min_state_nodes)}}}"
        dot_string += f"    {min_rank_string}\n"

    dot_string += "}"
    # print(dot_string)
    return dot_string


def get_numbered_grounded_extension(argumentation_framework):
    # Keep argument ID dictionary.
    argument_name_to_id = {}
    id_to_argument_name = {}
    for arg_id, argument in enumerate(argumentation_framework.arguments):
        argument_name_to_id[argument.name] = "a" + str(arg_id)
        id_to_argument_name["a" + str(arg_id)] = argument.name

    # Run clingo solver.
    ctl = clingo.Control()
    ctl.load(str(PATH_TO_ENCODINGS / "grounded_encoding.dl"))
    for argument in argumentation_framework.arguments:
        pos_fact = f"pos({argument_name_to_id[argument.name]})."
        ctl.add("base", [], pos_fact)
    for defeat in argumentation_framework.defeats:
        ctl.add(
            "base",
            [],
            f"attack({argument_name_to_id[defeat.from_argument.name]}, "
            f"{argument_name_to_id[defeat.to_argument.name]}).",
        )
    ctl.ground([("base", [])])
    models = []
    ctl.solve(on_model=lambda m: models.append(m.symbols(shown=True)))

    # Read output of clingo solver.
    atoms = models[0]
    number_by_argument = {}
    status_by_argument = {}
    for atom in atoms:
        if atom.name == "len":
            argument_name = id_to_argument_name[atom.arguments[1].name]
            if atom.arguments[0].name == "undefined":
                number_by_argument[argument_name] = "∞"
            else:
                number_by_argument[argument_name] = str(atom.arguments[2])
            status_by_argument[argument_name] = atom.arguments[0].name
    return status_by_argument, number_by_argument


def set_style(keyword, style, rm_edge):
    if rm_edge != None and keyword in rm_edge:
        return "invis"
    else:
        return style


def set_constraint_con(bool, con_type):
    if not bool:
        return 'constraint="false"'
    if con_type == "BU" and "BU" not in bool:
        return 'constraint="false"'
    elif con_type == "RD" and "RD" not in bool:
        return 'constraint="false"'
    else:
        return ""


def get_provenance(arg_framework, prov_type: str, node: str):
    """Executes a Clingo-based algorithm with given facts and a specific provenance type for a node.

    Args:
        facts (str): Facts to be loaded into Clingo.
        prov_type (str): Provenance type, one of {"PO", "AC", "PR"}.
        node (str): Target node for the algorithm.
    Returns:
        tuple: A tuple containing:
            - list of edges as "source,target" strings.
            - list of nodes as plain strings.
    """
    # Map provenance type to the corresponding prefix and edge predicate
    facts = "\n".join(
            [
                f'move("{attack.to_argument}","{attack.from_argument}").'
                for attack in arg_framework.defeats
            ]
        )
    
    prov_map = {
        "PO": ("pot_prov", "pot_edge"),
        "AC": ("act_prov", "act_edge"),
        "PR": ("pr_prov", "pr_edge")
    }
    
    if prov_type not in prov_map:
        raise ValueError(f"Invalid provenance type '{prov_type}'. Expected one of {list(prov_map.keys())}.")
    
    prov_prefix, prov_edges = prov_map[prov_type]
    
    
    # Initialize Clingo control with specific options
    ctl = clingo.Control(["--warn=none", "--opt-mode=optN"])
    ctl.configuration.solve.models = 0

    # Load facts and the algorithm into Clingo
    ctl.add("base", [], facts)
    ctl.add("base", [], f'start("{node}").')
    ctl.load(str(PATH_TO_ENCODINGS / "provenance_calculation.dl"))

    # Ground the program
    ctl.ground([("base", [])])
    edges = []
    nodes = set()

    # Callback function to extract relevant predicates and nodes
    def collect_results(model):
        for atom in model.symbols(atoms=True):
            if atom.name == prov_prefix and len(atom.arguments) == 2:
                source, target = atom.arguments
                edges.append(f"({target},{source})")  # Format edge as "source,target"
                nodes.add(str(source))
                nodes.add(str(target))
    
    nodes.add(f'"{node}"')# Solve and extract results
    ctl.solve(on_model=collect_results)
    
    return edges, list(nodes)


def get_local_view_rank(arg_framework, prov_arg):
    """
    Calculates the local view rank for a given argument.

    Args:
        arg_framework (ArgumentationFramework): The argumentation framework.
        prov_arg (str): The provenance argument.

    Returns:
        tuple: (rank_dict, rank_str) where rank_dict maps arguments to their ranks
               and rank_str is the formatted graphviz rank string
    """
    facts = "\n".join(
            [
                f'attacks("{attack.from_argument}","{attack.to_argument}").'
                for attack in arg_framework.defeats
            ]
        )
    # print(facts)
    ctl = clingo.Control(["--warn=none", "--opt-mode=optN"])
    ctl.configuration.solve.models = 0

    ctl.add("base", [], facts)
    # Match case of prov_arg with the original argument
    if any(str(attack.from_argument).isupper() 
           for attack in arg_framework.defeats):
        target_arg = prov_arg.upper()
    else:
        target_arg = prov_arg.lower()
    # print(target_arg)
    ctl.add("base", [], f'target("{target_arg}").')
    ctl.load(str(PATH_TO_ENCODINGS / "local_view_rank.dl"))
    ctl.ground([("base", [])])
    models = []
    ctl.solve(on_model=lambda m: models.append(m.symbols(shown=True)))
    
    rank_dict = {}
    atoms = models[0]
    for atom in atoms:
        if atom.name == "min_distance":
            arg = str(atom.arguments[0])
            rank = int(str(atom.arguments[1]))
            rank_dict[arg] = rank
    
    # Group nodes by their rank, including the target node at rank 0
    rank_groups = {0: [f'"{prov_arg}"']}  # Initialize with provenance argument at rank 0
    for arg, rank in rank_dict.items():
        if rank > 0:  # Skip the target node since we already added it
            if rank not in rank_groups:
                rank_groups[rank] = []
            rank_groups[rank].append(arg)

    return rank_groups


def highlight_dot_source(dot_source, highlight_nodes, prov_arg, prov_type, local_view, local_view_rank=None):
    """
    Processes a DOT source string and returns a modified version based on provenance type.
    
    Parameters:
        dot_source (str): Original DOT graph.
        highlight_nodes (list of str): List of nodes to keep unchanged.
        prov_arg (str): The provenance argument.
        prov_type (str): Type of provenance ("PO", "PR", "AC").
        local_view (bool): Whether to use local view.
        local_view_rank (dict, optional): Dictionary mapping ranks to lists of nodes.
                                        Example: {1: ['"D"', '"E"'], 2: ['"F"', '"G"']}

    Returns:
        str: Modified DOT source.
    """
    COLORS = {
        'light_gray': '#d3d3d3',
        'gray': '#bebebe',
        'border_gray': '#cccccc',
        'white': 'white',
        'black': 'black'
    }
    # print(local_view_rank)
    def is_highlighted_node(line):
        match = re.search(r'"([^"]+)"\s*\[', line)
        return match and f'"{match.group(1)}"' in highlight_nodes

    def is_highlighted_edge(line):
        edge_match = re.match(r'^\s*"([^"]+)"\s*->\s*"([^"]+)"', line)
        if edge_match:
            src, dst = f'"{edge_match.group(1)}"', f'"{edge_match.group(2)}"'
            return src in highlight_nodes and dst in highlight_nodes
        return False

    def process_node_line(line, stripped_line):
        # Skip the default node attributes line
        if 'node [fontname' in line:
            return line
            
        # Remove numbers and infinite symbols for PO and AC
        if prov_type in ["PO", "AC"]:
            line = re.sub(r'"([^"]+)\.(?:\d+|∞)"', r'"\1"', line)
        
        if not is_highlighted_node(stripped_line):
            new_line = line
            # If color exists, replace it
            if 'color=' in new_line:
                new_line = re.sub(r'color="[^"]*"', f'color="{COLORS["border_gray"]}"', new_line)
            else:
                # Add color if it doesn't exist
                new_line = new_line.replace('[', f'[color="{COLORS["border_gray"]}", ', 1)
                
            # Replace fillcolor if it exists
            if 'fillcolor=' in new_line:
                new_line = re.sub(r'fillcolor="[^"]*"', f'fillcolor="{COLORS["white"]}"', new_line)
            
            return new_line
        
        # For highlighted nodes, keep original line
        if prov_type == "PO":
            new_line = re.sub(r'fillcolor="[^"]*"', f'fillcolor="{COLORS["gray"]}"', line)
            if 'fillcolor=' not in new_line:
                new_line = new_line.replace('[', f'[fillcolor="{COLORS["gray"]}", ', 1)
            if 'style=' not in new_line:
                new_line = new_line.replace('[', '[style="filled", ', 1)
        else:
            new_line = line

        # Add penwidth for the chosen argument
        if f'"{prov_arg}"' in new_line and 'penwidth=' not in new_line:
            new_line = new_line.replace('[', '[penwidth="5", ', 1)
            
        return new_line

    def process_edge_line(line):
        # Check for dir=back in original line
        dir_back = False  # Initialize dir_back to False for all cases
        new_line = re.sub(r'\[.*?\]', '', line).strip()  # Remove all edge attributes
        
        # Extract source and target nodes
        match = re.match(r'^\s*"([^"]+)"\s*->\s*"([^"]+)"', new_line)
        if not match:
            return line
        
        src, dst = match.group(1), match.group(2)
        
        # Always apply rank-based handling when local_view is True, regardless of prov_type
        if local_view:
            # If original line had dir=back, normalize the direction first
            if 'dir=back' in line:
                src, dst = dst, src
                new_line = f'"{src}" -> "{dst}"'
            
            # Handle edge direction based on local_view_rank
            if local_view_rank:
                # Find ranks for source and target nodes
                src_rank = next((r for r, nodes in local_view_rank.items() if f'"{src}"' in nodes), None)
                dst_rank = next((r for r, nodes in local_view_rank.items() if f'"{dst}"' in nodes), None)
                
                # Handle special case for provenance argument (rank 0)
                if dst == prov_arg.strip('"'):
                    dst_rank = 0
                    
                # Keep dir=back only for edges from lower rank to higher rank
                # Only consider rank comparison if neither node is the provenance argument
                if src_rank is not None and dst_rank is not None:
                    if src_rank < dst_rank:
                        # Lower to higher rank: use dir=back and swap nodes
                        new_line = f'"{dst}" -> "{src}"'
                        dir_back = True
                    else:
                        # Ensure we use normal direction for all other cases
                        new_line = f'"{src}" -> "{dst}"'
                        dir_back = False
        else:
            # If not in local_view mode, preserve original dir=back
            dir_back = 'dir=back' in line
        
        if not is_highlighted_edge(line):
            attrs = [f'color="{COLORS["light_gray"]}"']
            if dir_back:
                attrs.append('dir=back')
            return new_line + f' [{", ".join(attrs)}]'
            
        if prov_type == "PO":
            attrs = ['color="black"']
            if dir_back:
                attrs.append('dir=back')
        elif prov_type == "AC":
            color_match = re.search(r'color="([^"]*)"', line)
            color = color_match.group(1) if color_match else COLORS["black"]
            attrs = [f'color="{color}"']
            if dir_back:
                attrs.append('dir=back')
        else:  # PR
            # For PR, preserve all attributes except dir=back
            color_match = re.search(r'color="([^"]*)"', line)
            style_match = re.search(r'style="([^"]*)"', line)
            fontcolor_match = re.search(r'fontcolor="([^"]*)"', line)
            arrowtail_match = re.search(r'arrowtail="([^"]*)"', line)
            arrowhead_match = re.search(r'arrowhead="([^"]*)"', line)
            label_match = re.search(r'(tail|head)label="([^"]*)"', line)
            
            attrs = []
            if color_match:
                attrs.append(f'color="{color_match.group(1)}"')
            if style_match:
                attrs.append(f'style="{style_match.group(1)}"')
            if fontcolor_match:
                attrs.append(f'fontcolor="{fontcolor_match.group(1)}"')
            if arrowtail_match:
                attrs.append(f'arrowtail="{arrowtail_match.group(1)}"')
            if arrowhead_match:
                attrs.append(f'arrowhead="{arrowhead_match.group(1)}"')
            if label_match:
                attrs.append(f'{label_match.group(1)}label="{label_match.group(2)}"')
            if dir_back:
                attrs.append('dir=back')
            
        return new_line + f' [{", ".join(attrs)}]'

    modified_lines = []
    in_rank_section = False
    rank_section_added = False
    
    for line in dot_source.split('\n'):
        stripped_line = line.strip()

        # Skip existing rank definitions when local_view is True
        if local_view and "rank =" in line:
            in_rank_section = True
            continue
        
        if in_rank_section:
            if not any(keyword in line for keyword in ["rank =", "}"]):
                continue
            if "}" in line:
                in_rank_section = False
                if not rank_section_added and local_view_rank:
                    # Add new rank definitions
                    for rank, nodes in sorted(local_view_rank.items()):
                        node_str = ' '.join(nodes)  # nodes are already in correct format ('"D"', '"E"', etc.)
                        modified_lines.append(f'    {{rank = same {node_str}}}')
                    rank_section_added = True

        # Process non-rank lines
        if not in_rank_section:
            if '->' not in stripped_line and '[' in stripped_line:
                modified_lines.append(process_node_line(line, stripped_line))
            elif '->' in stripped_line:
                modified_lines.append(process_edge_line(line))
            else:
                modified_lines.append(line)

    return "\n".join(modified_lines)


def highlight_critical_edges(dot_source, edges_to_highlight):
    """
    Highlights specified edges in red and dashed style in the DOT source.
    Also ensures nodes with infinite (∞) have dashed style and penwidth=1.5.
    
    Args:
        dot_source (str): The original DOT source string
        edges_to_highlight (list): List of edges to highlight, each edge is [from_arg, to_arg]
    
    Returns:
        str: Modified DOT source with highlighted edges
    """
    if not edges_to_highlight:
        return dot_source
        
    modified_source = dot_source
    
    # First handle nodes with infinite symbol
    lines = modified_source.split('\n')
    for i, line in enumerate(lines):
        if '.∞"' in line and '[' in line:
            if 'style=' in line:
                # Keep existing style attributes and add dashed if not present
                style_match = re.search(r'style="([^"]*)"', line)
                if style_match:
                    current_styles = style_match.group(1).split(',')
                    if 'dashed' not in current_styles:
                        current_styles.append('dashed')
                    new_style = ','.join(s.strip() for s in current_styles)
                    lines[i] = re.sub(r'style="[^"]*"', f'style="{new_style}"', line)
                    # Add penwidth if not present
                    if 'penwidth=' not in lines[i]:
                        lines[i] = lines[i].replace(']', ', penwidth=1.5]')
            else:
                # Add both style and penwidth attributes before the closing bracket
                lines[i] = line.replace(']', ', style="dashed", penwidth=1.5]')
    modified_source = '\n'.join(lines)
    
    # Then handle critical edges
    for edge in edges_to_highlight:
        from_arg, to_arg = edge
        # Look for the edge pattern in both directions (normal and dir=back)
        edge_patterns = [
            f'"{from_arg}" -> "{to_arg}"',
            f'"{to_arg}" -> "{from_arg}".*dir=back'
        ]
        
        for pattern in edge_patterns:
            edge_match = re.search(pattern, modified_source)
            if edge_match:
                edge_pos = edge_match.start()
                # Find the closing bracket of the edge attributes
                bracket_end = modified_source.find(']', edge_pos)
                if bracket_end != -1:
                    # Extract existing attributes
                    attrs_start = modified_source.find('[', edge_pos)
                    existing_attrs = modified_source[attrs_start+1:bracket_end]
                    
                    # Parse existing attributes
                    attrs = {}
                    for attr in re.findall(r'(\w+)="([^"]*)"', existing_attrs):
                        attrs[attr[0]] = attr[1]
                    
                    # Update attributes
                    attrs['color'] = '#ff0000'
                    if 'style' in attrs:
                        styles = attrs['style'].split(',')
                        if 'dashed' not in styles:
                            styles.append('dashed')
                        attrs['style'] = ','.join(s.strip() for s in styles)
                    else:
                        attrs['style'] = 'dashed'
                    
                    # Reconstruct attributes string
                    new_attrs = ' '.join(f'{k}="{v}"' for k, v in attrs.items())
                    
                    # Replace attributes in source
                    modified_source = (
                        modified_source[:attrs_start+1] +
                        new_attrs +
                        modified_source[bracket_end:]
                    )
                break  # Found the edge, no need to check other pattern
    
    return modified_source

def recalculate_fixed_args(arg_framework, dot_source):
    """
    Recalculates the grounded extension of an argumentation framework and updates the DOT source.
    
    Args:
        arg_framework (ArgumentationFramework): The argumentation framework to recalculate.
        dot_source (str): The original DOT source string.
    
    Returns:
        str: Modified DOT source with recalculated grounded extension.
    """ 
    # Get the new grounded extension and numbering
    status_dict, numbering_dict = get_numbered_grounded_extension(arg_framework)
    
    # Split dot source into lines and process node labels
    lines = dot_source.split('\n')
    modified_lines = []
    
    # Process existing lines
    for line in lines:
        # Skip any existing rank definitions
        if 'rank=' not in line:
            if '[' in line:
                if '->' in line:  # Edge definition
                    # Extract source and target nodes
                    match = re.match(r'^\s*"([^"]+)"\s*->\s*"([^"]+)"', line)
                    if match:
                        source, target = match.group(1), match.group(2)
                        source_val = numbering_dict.get(source)
                        target_val = numbering_dict.get(target)
                        
                        # Extract existing attributes
                        attrs_match = re.search(r'\[(.*)\]', line)
                        if attrs_match:
                            existing_attrs = attrs_match.group(1)
                            
                            # Replace existing labels with empty ones
                            existing_attrs = re.sub(r'taillabel="[^"]*"', 'taillabel=""', existing_attrs)
                            existing_attrs = re.sub(r'headlabel="[^"]*"', 'headlabel=""', existing_attrs)
                            
                            # For dir=back edges, the actual source is the target node
                            has_dir_back = 'dir=back' in existing_attrs
                            actual_source_val = target_val if has_dir_back else source_val
                            actual_target_val = source_val if has_dir_back else target_val
                            
                            # Check if style is dotted
                            is_dotted = 'style="dotted"' in existing_attrs or 'style= "dotted"' in existing_attrs
                            if not is_dotted:
                                is_solid = 'style="solid"' in existing_attrs or 'style= "solid"' in existing_attrs
                                
                                if is_solid and actual_source_val > actual_target_val:
                                    existing_attrs = re.sub(r'style\s*=\s*"[^"]*"', 'style="dashed"', existing_attrs)
                                elif not is_solid and actual_source_val < actual_target_val:
                                    existing_attrs = re.sub(r'style\s*=\s*"[^"]*"', 'style="solid"', existing_attrs)
                                
                                # Handle direction based on numbers
                                if actual_source_val > actual_target_val:
                                    if not has_dir_back:
                                        existing_attrs += ', dir=back'
                                        line = f'    "{target}" -> "{source}" [{existing_attrs}]'
                                    else:
                                        line = f'    "{source}" -> "{target}" [{existing_attrs}]'
                                else:
                                    line = f'    "{source}" -> "{target}" [{existing_attrs}]'
                            else:
                                line = f'    "{source}" -> "{target}" [{existing_attrs}]'
                elif 'label=' in line and '∞' in line:  # Node definition with infinite label
                    # Extract argument name
                    arg_name = line.split('"')[1]
                    if arg_name in numbering_dict:
                        # Replace "∞" with the new number and add prime
                        new_number = numbering_dict[arg_name]
                        line = line.replace('.∞"', f'.{new_number}′"')  # Using unicode prime symbol
            modified_lines.append(line)
    
    # Find the last closing brace
    while modified_lines[-1].strip() == '}':
        modified_lines.pop()
    
    # Group nodes by their numbers
    number_groups = {}
    for arg, number in numbering_dict.items():
        if number not in number_groups:
            number_groups[number] = []
        number_groups[number].append(arg)
    
    # Add rank definitions before the final closing brace
    for number, args in sorted(number_groups.items(), key=lambda x: int(x[0]) if x[0] != '∞' else float('inf')):
        if args:
            node_list = '" "'.join(args)
            modified_lines.append(f'    {{ rank=same; "{node_list}" }}')
    
    # Add back the closing brace
    modified_lines.append('}')
    
    return '\n'.join(modified_lines)


