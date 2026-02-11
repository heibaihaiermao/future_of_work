import json
from typing import Any, Dict, List, Union
from collections import defaultdict

class JSONSchemaIdentifier:
    """Identify and generate schema from JSON documents"""
    
    def __init__(self):
        self.schema = {}
    
    def identify_type(self, value: Any) -> str:
        """Identify the JSON type of a value"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        return "unknown"
    
    def analyze_array(self, arr: List) -> Dict:
        """Analyze array structure"""
        if not arr:
            return {"type": "array", "items": {}}
        
        # Track types of items
        type_counts = defaultdict(int)
        item_schemas = []
        
        for item in arr:
            item_type = self.identify_type(item)
            type_counts[item_type] += 1
            
            if item_type == "object":
                item_schemas.append(self.analyze_object(item))
            elif item_type == "array":
                item_schemas.append(self.analyze_array(item))
        
        # Determine item schema
        if len(type_counts) == 1:
            single_type = list(type_counts.keys())[0]
            if single_type == "object" and item_schemas:
                items = self.merge_object_schemas(item_schemas)
            elif single_type == "array" and item_schemas:
                items = item_schemas[0]
            else:
                items = {"type": single_type}
        else:
            # Mixed types
            items = {"type": list(type_counts.keys())}
        
        return {"type": "array", "items": items}
    
    def analyze_object(self, obj: Dict) -> Dict:
        """Analyze object structure"""
        properties = {}
        
        for key, value in obj.items():
            value_type = self.identify_type(value)
            
            if value_type == "object":
                properties[key] = self.analyze_object(value)
            elif value_type == "array":
                properties[key] = self.analyze_array(value)
            else:
                properties[key] = {"type": value_type}
        
        return {
            "type": "object",
            "properties": properties
        }
    
    def merge_object_schemas(self, schemas: List[Dict]) -> Dict:
        """Merge multiple object schemas"""
        if not schemas:
            return {"type": "object", "properties": {}}
        
        merged_properties = {}
        
        for schema in schemas:
            if "properties" in schema:
                for prop, prop_schema in schema["properties"].items():
                    if prop not in merged_properties:
                        merged_properties[prop] = prop_schema
        
        return {
            "type": "object",
            "properties": merged_properties
        }
    
    def generate_schema(self, json_data: Union[str, Dict]) -> Dict:
    #def generate_schema(self, jdoc) -> Dict:

        """Generate schema from JSON data"""
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)

            except json.JSONDecodeError:
                with open(json_data, 'r', encoding="utf-8-sig") as fil:
                    json_data = json.load(fil)
        
        json_type = self.identify_type(json_data)
        
        if json_type == "object":
            self.schema = self.analyze_object(json_data)
        elif json_type == "array":
            self.schema = self.analyze_array(json_data)
        else:
            self.schema = {"type": json_type}
        
        return self.schema
    
    def to_json_schema(self, draft: str = "7") -> Dict:
        """Convert to JSON Schema Draft format"""
        return {
            "$schema": f"http://json-schema.org/draft-{draft}/schema#",
            **self.schema
        }
    
    def pretty_print(self) -> str:
        """Pretty print the schema"""
        return json.dumps(self.schema, indent=2)


# Example usage
if __name__ == "__main__":
    # Example JSON documents
    examples = [
        # Example 1: Simple object
        {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com",
            "active": True
        },
        # Example 2: Nested object with array
        {
            "id": 1,
            "title": "Blog Post",
            "content": "Lorem ipsum",
            "tags": ["python", "json", "schema"],
            "author": {
                "name": "Jane",
                "email": "jane@example.com"
            },
            "comments": [
                {"user": "Bob", "text": "Great post!"},
                {"user": "Alice", "text": "Thanks for sharing"}
            ]
        },
        # Example 3: Array of objects
        [
            {"id": 1, "name": "Alice", "score": 95.5},
            {"id": 2, "name": "Bob", "score": 87.3},
            {"id": 3, "name": "Charlie", "score": 92.1}
        ]
    ]


    from sys import argv
    jdoc = argv[1]


    identifier = JSONSchemaIdentifier()
    schema = identifier.generate_schema(jdoc)
    
    #for i, example in enumerate(examples, 1):
    #    print(f"\n{'='*60}")
    #    print(f"Example {i}:")
    #    print(f"{'='*60}")
    #    print("\nJSON Input:")
    #    print(json.dumps(example, indent=2))
    #    
    #    
    #    print("\nGenerated Schema:")
    #    print(identifier.pretty_print())
    #    
    #    print("\nJSON Schema Draft 7:")
    #    print(json.dumps(identifier.to_json_schema(), indent=2))
