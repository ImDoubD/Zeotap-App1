## Objective
This Rule Engine application evaluates user eligibility based on dynamic rules created using an Abstract Syntax Tree (AST). The application enables creating, combining, modifying, and evaluating rules based on user attributes (e.g., age, department, income, etc.).

## Technology Stack
- Backend Framework: FastAPI (Python)
- Database: SQLite (SQLAlchemy ORM for data management)
- Data Structure for Rules: AST represented by a custom Node class
- Dependencies: FastAPI, SQLAlchemy, Pydantic

## Features
- Create Rule - Define new rules and store them in an AST format.
- Combine Rules - Combine multiple rules using logical operators (AND, OR).
- Modify Rule - Update existing rules to modify conditions or logic.
- Evaluate Rule - Test user data against rules to check eligibility.

## Code Structure
### **main.py**
    The main application file defines the API endpoints and controls the rule management flow.
### **API Endpoints:**
  - POST /create_rule: Input= Rule String in query params. Creates a rule, parses it into an AST, and saves it in the database.
  - POST /combine_rules: Input = List of Existing Rule IDs. Combines multiple rules using logical operators.
  - POST /evaluate_rule: Input = {Rule id, user_data}. Evaluates a rule against user data.
  - GET /fetch-rules: Fetches all rules.
  - PUT /modify_rule:Input = Rule_id, rule_string (new) in query params. Updates an existing rule's conditions.
### **ast_parser.py**
  - Node Class
    - The Node class represents a single node in the AST, which could be an operator (like AND or OR) or an operand (a condition like age > 30). Each Node contains:
    - type: Specifies whether the node is an "operator" (e.g., AND, OR) or "operand" (e.g., age > 30).
    - value: Holds the value of the node. For an operator node, this is the operator (e.g., AND or OR), and for an operand node, this is the condition (e.g., age >30).
    - left and right: Point to the child nodes. Operator nodes use these to represent the left and right conditions of the logical expression.
  - Creating a Rule (createRule Function)
    - The createRule function parses a rule string into an AST structure by splitting conditions based on logical operators.
    - String Parsing: It checks if the rule contains AND or OR, and splits the rule string into left and right conditions based on the detected operator.
    - AST Construction:
      - If an AND or OR operator is found, the root node is created with type = "operator" and value set to the operator (AND or OR).
      - The left and right conditions become child nodes of this root node, each with type = "operand" and a condition (like age > 30) as value.
    - Single Condition: If the rule contains no logical operator, it is treated as a single operand node with the condition as its value.
    - **Example:** string = age > 30 AND department = 'Sales', will look like this below \
      ![image](https://github.com/user-attachments/assets/7a429220-475e-4e76-b0a3-2faf1ce70a0a)
  - Combining Rules (combineRules Function)
    - The combineRules function merges multiple ASTs into a single AST with a specified operator (AND or OR).
      - Input: Takes a list of Node objects (ASTs for individual rules) and an operator.
      - Combination Logic:
        - The function creates a root node with type = "operator" and value as the specified operator.
        - For each AST in the list:
          - The first AST is assigned as the left child of the root node.
          - Subsequent ASTs are linked to the right side. If there are multiple ASTs to combine, it recursively nests them, ensuring a consistent operator throughout.
    - **Example:** string1 = age > 30, string2 = salary > 50000 with AND will look like this below, \
      ![image](https://github.com/user-attachments/assets/8938cb4e-1567-4808-ba9b-69ed8e1aff79)
  - Evaluating a Rule (evaluateRule Function)
    - The evaluateRule function recursively evaluates an AST against user-provided data to see if it meets the rule’s conditions.
      - Operand Nodes: The function interprets operand nodes (conditions like age > 30) and checks them against the data dictionary.
        - Comparison Parsing: It detects the comparison operator (>=, <=, >, <, ==, =) and splits the condition into an attribute and a value.
        - Validation and Comparison: It retrieves the attribute's value from data, validates its existence, and performs the comparison.
        - Special Case: = is used for string comparisons, like matching department names.
      - Operator Nodes: For nodes with logical operators (AND, OR):
        - The function recursively evaluates the left and right child nodes.
        - The result is determined by applying the operator (AND returns True only if both conditions are True, while OR returns True if either condition is True).
    - **Example:** Suppose the AST represents the rule (age > 30 AND department = 'Sales') OR (salary > 50000), and data is {"age": 35, "department": "Sales", "salary": 45000}: \
        1. The evaluateRule function would first evaluate age > 30 and department = 'Sales'. \
        2. Since both conditions are True, the left side of the OR is True. \
        3. Therefore, the rule returns True, regardless of the salary condition.

### **models.py**
  - Defines the database schema for the Rule table. Each rule includes:
    - id: Unique identifier.
    - rule_string: Original rule as a string.
    - ast_json: JSON representation of the AST.
### **schemas.py**
  - Defines data validation using Pydantic for API requests, including:
    - CombineRulesRequest: Combines multiple rules using an operator.
    - EvaluateRuleRequest: Evaluates a rule with user data.
### **Error Handling & Validation**
  - Invalid Rule String: If a rule string is invalid or contains unsupported operators, an error response is returned.
  - Missing Data Attributes: When evaluating a rule, missing attributes in the user data raise a descriptive error.
  - Rule Not Found: If a rule ID is invalid during retrieval, a 404 error is raised.
  - Rule Modification: During modification, the rule string is validated before updating the AST.
