#!/usr/bin/env python3
"""
Validate services.json against schema.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

def load_json(filepath: Path) -> Dict[str, Any]:
    """Load a JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def validate_structure(services: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """Basic structure validation"""
    errors = []
    
    # Check required top-level fields
    required_fields = ['version', 'lastUpdated', 'services', 'categories']
    for field in required_fields:
        if field not in services:
            errors.append(f"Missing required field: {field}")
    
    # Validate services
    if 'services' in services:
        service_ids = set()
        slugs = set()
        
        for i, service in enumerate(services['services']):
            # Check for duplicate IDs
            if service.get('serviceId') in service_ids:
                errors.append(f"Duplicate serviceId: {service.get('serviceId')}")
            service_ids.add(service.get('serviceId'))
            
            # Check for duplicate slugs
            if service.get('slug') in slugs:
                errors.append(f"Duplicate slug: {service.get('slug')}")
            slugs.add(service.get('slug'))
            
            # Check required service fields
            required_service_fields = ['serviceId', 'slug', 'name', 'provider', 'category', 'metadata']
            for field in required_service_fields:
                if field not in service:
                    errors.append(f"Service {i} missing required field: {field}")
    
    return errors

def validate_categories(services: Dict[str, Any]) -> List[str]:
    """Validate category references"""
    errors = []
    
    # Get valid category IDs
    valid_categories = set()
    if 'categories' in services:
        valid_categories = {cat['id'] for cat in services['categories']}
    
    # Check each service's category
    if 'services' in services:
        for service in services['services']:
            if 'category' in service and service['category'] not in valid_categories:
                errors.append(f"Service {service.get('serviceId')} has invalid category: {service['category']}")
    
    return errors

def validate_urls(services: Dict[str, Any]) -> List[str]:
    """Validate URL formats"""
    errors = []
    warnings = []
    
    if 'services' in services:
        for service in services['services']:
            # Check website URL
            website = service.get('website')
            if website and not website.startswith(('http://', 'https://')):
                errors.append(f"Service {service.get('serviceId')} has invalid website URL: {website}")
    
    return errors

def generate_stats(services: Dict[str, Any]) -> Dict[str, Any]:
    """Generate statistics about the repository"""
    stats = {
        'total_services': len(services.get('services', [])),
        'total_categories': len(services.get('categories', [])),
        'services_per_category': {},
        'pricing_models': {},
        'verification_status': {}
    }
    
    for service in services.get('services', []):
        # Count by category
        category = service.get('category', 'unknown')
        stats['services_per_category'][category] = stats['services_per_category'].get(category, 0) + 1
        
        # Count by pricing model
        pricing_model = service.get('pricing', {}).get('model', 'unknown')
        stats['pricing_models'][pricing_model] = stats['pricing_models'].get(pricing_model, 0) + 1
        
        # Count by verification status
        status = service.get('metadata', {}).get('verificationStatus', 'unknown')
        stats['verification_status'][status] = stats['verification_status'].get(status, 0) + 1
    
    return stats

def main():
    """Main validation function"""
    # Get paths
    script_dir = Path(__file__).parent
    repo_dir = script_dir.parent
    
    schema_path = repo_dir / 'schema.json'
    services_path = repo_dir / 'services.json'
    
    # Load files
    try:
        schema = load_json(schema_path)
        services = load_json(services_path)
    except Exception as e:
        print(f"Error loading files: {e}")
        sys.exit(1)
    
    # Run validations
    errors = []
    errors.extend(validate_structure(services, schema))
    errors.extend(validate_categories(services))
    errors.extend(validate_urls(services))
    
    # Print results
    if errors:
        print("Validation Errors:")
        for error in errors:
            print(f"  ❌ {error}")
        print(f"\nTotal errors: {len(errors)}")
        sys.exit(1)
    else:
        print("✅ Validation passed!")
        
        # Print statistics
        stats = generate_stats(services)
        print("\nRepository Statistics:")
        print(f"  Total services: {stats['total_services']}")
        print(f"  Total categories: {stats['total_categories']}")
        
        print("\n  Services per category:")
        for cat, count in sorted(stats['services_per_category'].items()):
            print(f"    {cat}: {count}")
        
        print("\n  Pricing models:")
        for model, count in sorted(stats['pricing_models'].items()):
            print(f"    {model}: {count}")
        
        print("\n  Verification status:")
        for status, count in sorted(stats['verification_status'].items()):
            print(f"    {status}: {count}")

if __name__ == '__main__':
    main()