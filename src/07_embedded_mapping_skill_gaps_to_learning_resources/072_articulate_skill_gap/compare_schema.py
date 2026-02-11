import json
from typing import Any, Dict, List, Set, Tuple
from enum import Enum

class DifferenceType(Enum):
    """Types of schema differences"""
    TYPE_MISMATCH = "Type Mismatch"
    MISSING_PROPERTY = "Missing Property"
    EXTRA_PROPERTY = "Extra Property"
    ARRAY_ITEM_MISMATCH = "Array Item Type Mismatch"
    CARDINALITY_CHANGE = "Cardinality Change"
    REQUIRED_CHANGE = "Required Change"

class SchemaComparator:
    """Compare and analyze differences between two JSON schemas"""
    
    def __init__(self):
        self.differences = []
        self.compatibility_score = 100.0
    
    def compare_schemas(self, schema1: Dict, schema2: Dict) -> Dict:
        """
        Compare two schemas and return detailed differences
        
        Args:
            schema1: First schema
            schema2: Second schema
        
        Returns:
            Dictionary containing comparison results
        """
        self.differences = []
        self.compatibility_score = 100.0
        
        self._compare_nodes(schema1, schema2, path="root")
        
        return {
            "compatibility_score": self.compatibility_score,
            "total_differences": len(self.differences),
            "differences": self.differences,
            "is_compatible": self.compatibility_score >= 70
        }
    
    def _compare_nodes(self, node1: Any, node2: Any, path: str) -> None:
        """Recursively compare schema nodes"""
        
        # Get types
        type1 = node1.get("type") if isinstance(node1, dict) else None
        type2 = node2.get("type") if isinstance(node2, dict) else None
        
        # Compare types
        if type1 != type2:
            self._add_difference(
                DifferenceType.TYPE_MISMATCH,
                path,
                f"Type changed from '{type1}' to '{type2}'"
            )
            return
        
        # If both are objects, compare properties
        if type1 == "object":
            self._compare_objects(node1, node2, path)
        
        # If both are arrays, compare items
        elif type1 == "array":
            self._compare_arrays(node1, node2, path)
    
    def _compare_objects(self, obj1: Dict, obj2: Dict, path: str) -> None:
        """Compare object schemas"""
        props1 = obj1.get("properties", {})
        props2 = obj2.get("properties", {})
        
        required1 = set(obj1.get("required", []))
        required2 = set(obj2.get("required", []))
        
        all_keys = set(props1.keys()) | set(props2.keys())
        
        for key in all_keys:
            property_path = f"{path}.{key}"
            
            # Check for missing properties
            if key not in props1 and key in props2:
                self._add_difference(
                    DifferenceType.MISSING_PROPERTY,
                    property_path,
                    "Property added in schema2"
                )
            
            # Check for extra properties
            elif key in props1 and key not in props2:
                self._add_difference(
                    DifferenceType.EXTRA_PROPERTY,
                    property_path,
                    "Property removed in schema2"
                )
            
            # Check for required changes
            elif key in required1 and key not in required2:
                self._add_difference(
                    DifferenceType.REQUIRED_CHANGE,
                    property_path,
                    "Property changed from required to optional"
                )
            
            elif key not in required1 and key in required2:
                self._add_difference(
                    DifferenceType.REQUIRED_CHANGE,
                    property_path,
                    "Property changed from optional to required"
                )
            
            # Recursively compare nested properties
            if key in props1 and key in props2:
                self._compare_nodes(props1[key], props2[key], property_path)
    
    def _compare_arrays(self, arr1: Dict, arr2: Dict, path: str) -> None:
        """Compare array schemas"""
        items1 = arr1.get("items", {})
        items2 = arr2.get("items", {})
        
        # Handle cases where items is a list of types
        if isinstance(items1, list) and isinstance(items2, list):
            if len(items1) != len(items2):
                self._add_difference(
                    DifferenceType.CARDINALITY_CHANGE,
                    f"{path}[items]",
                    f"Array item tuple length changed from {len(items1)} to {len(items2)}"
                )
        
        # Compare item types
        elif items1 and items2:
            type1 = items1.get("type") if isinstance(items1, dict) else None
            type2 = items2.get("type") if isinstance(items2, dict) else None
            
            if type1 != type2:
                self._add_difference(
                    DifferenceType.ARRAY_ITEM_MISMATCH,
                    f"{path}[items]",
                    f"Array item type changed from '{type1}' to '{type2}'"
                )
            else:
                self._compare_nodes(items1, items2, f"{path}[items]")
    
    def _add_difference(self, diff_type: DifferenceType, path: str, description: str) -> None:
        """Record a difference and update compatibility score"""
        
        # Scoring impact based on severity
        severity_scores = {
            DifferenceType.TYPE_MISMATCH: 25,
            DifferenceType.MISSING_PROPERTY: 10,
            DifferenceType.EXTRA_PROPERTY: 5,
            DifferenceType.ARRAY_ITEM_MISMATCH: 20,
            DifferenceType.CARDINALITY_CHANGE: 15,
            DifferenceType.REQUIRED_CHANGE: 10,
        }
        
        self.compatibility_score -= severity_scores.get(diff_type, 5)
        self.compatibility_score = max(0, self.compatibility_score)
        
        self.differences.append({
            "type": diff_type.value,
            "path": path,
            "description": description,
            "severity": self._get_severity(diff_type)
        })
    
    def _get_severity(self, diff_type: DifferenceType) -> str:
        """Determine severity level"""
        high_severity = {
            DifferenceType.TYPE_MISMATCH,
            DifferenceType.ARRAY_ITEM_MISMATCH,
            DifferenceType.CARDINALITY_CHANGE
        }
        medium_severity = {
            DifferenceType.REQUIRED_CHANGE,
            DifferenceType.MISSING_PROPERTY
        }
        
        if diff_type in high_severity:
            return "HIGH"
        elif diff_type in medium_severity:
            return "MEDIUM"
        return "LOW"
    
    def get_summary(self) -> str:
        """Get a text summary of differences"""
        if not self.differences:
            return "✓ Schemas are identical!"
        
        summary = f"\n{'='*70}\n"
        summary += f"SCHEMA COMPARISON SUMMARY\n"
        summary += f"{'='*70}\n"
        summary += f"Compatibility Score: {self.compatibility_score:.1f}%\n"
        summary += f"Total Differences: {len(self.differences)}\n"
        summary += f"{'='*70}\n\n"
        
        # Group by severity
        high = [d for d in self.differences if d["severity"] == "HIGH"]
        medium = [d for d in self.differences if d["severity"] == "MEDIUM"]
        low = [d for d in self.differences if d["severity"] == "LOW"]
        
        if high:

            summary += f" HIGH SEVERITY ({len(high)}):\n"
            for diff in high:
                summary += f"  • {diff['path']}: {diff['description']}\n"
            summary += "\n"
        
        if medium:
            summary += f" MEDIUM SEVERITY ({len(medium)}):\n"
            for diff in medium:
                summary += f"  • {diff['path']}: {diff['description']}\n"
            summary += "\n"
        
        if low:
            summary += f" LOW SEVERITY ({len(low)}):\n"
            for diff in low:
                summary += f"  • {diff['path']}: {diff['description']}\n"
            summary += "\n"
        
        summary += f"{'='*70}\n"
        return summary


class SchemaAnalyzer:
    """Analyze relationships between schemas"""
    
    @staticmethod
    def is_backward_compatible(old_schema: Dict, new_schema: Dict) -> bool:
        """
        Check if new schema is backward compatible with old schema
        (old clients can still work with new schema)
        """
        comparator = SchemaComparator()
        result = comparator.compare_schemas(old_schema, new_schema)
        
        # Backward compatible if:
        # - No required properties were added
        # - No properties were removed
        # - No types were changed
        
        incompatible_types = [
            "Type Mismatch",
            "Missing Property",
            "Required Change"
        ]
        
        for diff in result["differences"]:
            if diff["type"] in incompatible_types:
                if diff["type"] == "Required Change" and "required to optional" not in diff["description"]:
                    return False
                elif diff["type"] != "Required Change":
                    return False
        
        return True
    
    @staticmethod
    def get_schema_diff_report(schema1: Dict, schema2: Dict, 
                               schema1_name: str = "Schema 1",
                               schema2_name: str = "Schema 2") -> str:
        """Generate a detailed diff report"""
        
        comparator = SchemaComparator()
        result = comparator.compare_schemas(schema1, schema2)
        
        report = f"\n{'='*70}\n"
        report += f"DETAILED SCHEMA DIFFERENCE REPORT\n"
        report += f"Comparing: {schema1_name} vs {schema2_name}\n"
        report += f"{'='*70}\n\n"
        
        report += comparator.get_summary()
        
        if result["differences"]:
            report += "\nDETAILED DIFFERENCES:\n"
            report += f"{'-'*70}\n"
            for i, diff in enumerate(result["differences"], 1):
                report += f"\n{i}. [{diff['severity']}] {diff['type']}\n"
                report += f"   Path: {diff['path']}\n"
                report += f"   Issue: {diff['description']}\n"
        
        backward_compatible = SchemaAnalyzer.is_backward_compatible(schema1, schema2)
        report += f"\n{'='*70}\n"
        report += f"Backward Compatible: {'✓ YES' if backward_compatible else '✗ NO'}\n"
        report += f"{'='*70}\n"
        
        return report


# Example usage
if __name__ == "__main__":
    # Schema 1: Original
    schema1 = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string"},
            "age": {"type": "integer"},
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"}
                }
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["id", "name", "email"]
    }
    
    # Schema 2: Modified version
    schema2 = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string"},
            "phone": {"type": "string"},  # New property
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "zip": {"type": "string"}  # New nested property
                }
            },
            "tags": {
                "type": "array",
                "items": {"type": "integer"}  # Changed type!
            }
        },
        "required": ["id", "name", "email", "phone"]  # phone now required
    }
    
    # Compare schemas
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Schema Comparison")
    print("="*70)
    
    comparator = SchemaComparator()
    result = comparator.compare_schemas(schema1, schema2)
    print(comparator.get_summary())
    print(json.dumps(result, indent=2, default=str))
    
    # Generate detailed report
    print(SchemaAnalyzer.get_schema_diff_report(
        schema1, schema2,
        "User Schema v1",
        "User Schema v2"
    ))
    
    # Example 2: Identical schemas
    print("\n" + "="*70)
    print("EXAMPLE 2: Comparing Identical Schemas")
    print("="*70)
    
    schema3 = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"}
        }
    }
    
    schema4 = schema3.copy()
    
    comparator2 = SchemaComparator()
    result2 = comparator2.compare_schemas(schema3, schema4)
    print(comparator2.get_summary())
    
    # Example 3: Backward compatibility check
    print("\n" + "="*70)
    print("EXAMPLE 3: Backward Compatibility Analysis")
    print("="*70)
    
    old_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"}
        },
        "required": ["id", "name"]
    }
    
    new_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string"}  # Optional new field
        },
        "required": ["id", "name"]
    }
    
    is_compatible = SchemaAnalyzer.is_backward_compatible(old_schema, new_schema)
    print(f"Is backward compatible: {is_compatible}")
    print(SchemaAnalyzer.get_schema_diff_report(
        old_schema, new_schema,
        "Old API Schema",
        "New API Schema"
    ))
