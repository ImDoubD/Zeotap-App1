from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models import Rule
from database import get_db
from ast_parser import createRule, combineRules, evaluateRule, Node
from schemas import CombineRulesRequest, EvaluateRuleRequest


app = FastAPI()

# Utility function to convert Node to dict
def node_to_dict(node):
    return {
        "type": node.type,
        "value": node.value,
        "left": node_to_dict(node.left) if node.left else None,
        "right": node_to_dict(node.right) if node.right else None
    }

# Utility function to convert dict to Node
def dict_to_node(data):
    if data is None:
        return None
    node = Node(data["type"], data["value"])
    node.left = dict_to_node(data["left"])
    node.right = dict_to_node(data["right"])
    return node

# Create a new rule
@app.post("/create_rule/")
def create_rule(
    rule_string: str = Query(...), 
    db: Session = Depends(get_db)
):
    try:
        ast = createRule(rule_string)
        ast_json = node_to_dict(ast) # AST to json

        # Saved in the database 
        new_rule = Rule(rule_string=rule_string, ast_json=ast_json)
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        return {"id": new_rule.id, "rule_string": rule_string, "ast": ast_json}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Combine new rule
@app.post("/combine_rules/")
def combine_rules(
    request: CombineRulesRequest,
    db: Session = Depends(get_db)
):
    try:
        rule_nodes = []
        rule_strings = []

        for rule_id in request.rules:
            rule = db.query(Rule).filter(Rule.id == rule_id).first()
            if not rule:
                raise HTTPException(status_code=404, detail=f"Rule with id {rule_id} not found")

            rule_ast = dict_to_node(rule.ast_json)  # AST JSON to Node
            rule_nodes.append(rule_ast)
            rule_strings.append(rule.rule_string) 

        # Combined ASTs
        combined_ast = combineRules(rule_nodes, request.operator)
        combined_ast_json = node_to_dict(combined_ast)  

        combined_rule_string = f" {request.operator} ".join(rule_strings)

        # Saved the combined rule into the database
        new_combined_rule = Rule(
            rule_string=combined_rule_string,
            ast_json=combined_ast_json
        )
        db.add(new_combined_rule)
        db.commit()
        db.refresh(new_combined_rule)

        return {
            "id": new_combined_rule.id,
            "combined_rule_string": combined_rule_string,
            "combined_ast": combined_ast_json
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in combining rules: {str(e)}")
    

# eveluate new rule
@app.post("/evaluate_rule/")
def evaluate_rule(
    request: EvaluateRuleRequest,
    db: Session = Depends(get_db)
):
    try:
        rule = db.query(Rule).filter(Rule.id == request.rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")

        ast = dict_to_node(rule.ast_json)
        result = evaluateRule(ast, request.user_data)
        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
@app.put("/modify_rule/")
def modify_rule(
    rule_id: int = Query(...),
    rule_string: str = Query(...),
    db: Session = Depends(get_db)
):
    try:
        rule = db.query(Rule).filter(Rule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")

        # Updated the rule_string
        rule.rule_string = rule_string
        # (Re)created the AST for the new rule string
        ast = createRule(rule_string)
        rule.ast_json = node_to_dict(ast)

        db.commit()
        db.refresh(rule)
        return {
            "id": rule.id,
            "rule_string": rule.rule_string,
            "ast": rule.ast_json
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
