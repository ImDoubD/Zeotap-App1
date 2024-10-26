from typing import List

class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.type = node_type
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Node({self.type}, {self.value})"

rule_store = {}

def createRule(ruleString):
    if "AND" in ruleString:
        connections = ruleString.split("AND")
        left = connections[0].strip()
        right = connections[1].strip()
        root = Node("operator", "AND")
        root.left = Node("operand", left) 
        root.right = Node("operand", right)
    elif "OR" in ruleString:
        connections = ruleString.split("OR")
        left = connections[0].strip()
        right = connections[1].strip()
        root = Node("operator", "OR")
        root.left = Node("operand", left) 
        root.right = Node("operand", right)
    else:
        root = Node("operand", ruleString.strip())

    return root

def combineRules(rules: List[Node], operator="AND") -> Node:
    if not rules:
        raise ValueError("No rules provided for combination.")

    combinedRoot = Node("operator", operator)
    curr = combinedRoot

    for i, rule in enumerate(rules):
        if i == 0:
            curr.left = rule
        else:
            curr.right = rule
            if i < len(rules) - 1:
                newNode = Node("operator", operator)
                curr.right = newNode
                curr = newNode

    return combinedRoot

def evaluateRule(ast, data):
    if ast.type == "operand":
        ruleCondition = ast.value.strip()

        if ">=" in ruleCondition:
            attribute, value = ruleCondition.split(">=")
            attribute = attribute.strip()
            value = int(value.strip())
            if attribute not in data:
                raise ValueError(f"Missing attribute '{attribute}' in user data")
            return data[attribute] >= value

        elif "<=" in ruleCondition:
            attribute, value = ruleCondition.split("<=")
            attribute = attribute.strip()
            value = int(value.strip())
            if attribute not in data:
                raise ValueError(f"Missing attribute '{attribute}' in user data")
            return data[attribute] <= value

        elif ">" in ruleCondition:
            attribute, value = ruleCondition.split(">")
            attribute = attribute.strip()
            value = int(value.strip())
            if attribute not in data:
                raise ValueError(f"Missing attribute '{attribute}' in user data")
            return data[attribute] > value

        elif "<" in ruleCondition:
            attribute, value = ruleCondition.split("<")
            attribute = attribute.strip()
            value = int(value.strip())
            if attribute not in data:
                raise ValueError(f"Missing attribute '{attribute}' in user data")
            return data[attribute] < value

        elif "==" in ruleCondition:
            attribute, value = ruleCondition.split("==")
            attribute = attribute.strip()
            value = int(value.strip())
            if attribute not in data:
                raise ValueError(f"Missing attribute '{attribute}' in user data")
            return data[attribute] == value
        
        if "=" in ruleCondition:
            attribute, value = ruleCondition.split("=")
            attribute = attribute.strip()
            value = value.strip().strip('"').strip("'")
            print("Att, Val ", attribute, value)
            if attribute not in data:
                raise ValueError(f"Missing attribute '{attribute}' in user data")
            # String comparison for department
            if attribute == "department":
                return data[attribute] == value

    elif ast.type == "operator":
        leftPart = evaluateRule(ast.left, data)
        rightPart = evaluateRule(ast.right, data)

        if ast.value == "AND":
            return leftPart and rightPart
        elif ast.value == "OR":
            return leftPart or rightPart

    return False