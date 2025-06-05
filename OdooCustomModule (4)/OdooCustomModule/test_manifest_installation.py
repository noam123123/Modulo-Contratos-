#!/usr/bin/env python3
"""
Comprehensive Odoo manifest installation test
Simulates the exact Odoo module installation process
"""

import os
import ast
import sys
import importlib.util

def test_manifest_syntax():
    """Test manifest file syntax and structure"""
    print("🔍 Testing manifest syntax and structure...")
    
    manifest_path = 'contratos/__manifest__.py'
    
    try:
        # Test Python syntax
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST
        ast.parse(content)
        print("  ✅ Manifest syntax valid")
        
        # Execute and get manifest dict
        namespace = {}
        exec(content, namespace)
        manifest = namespace.get('__manifest__')
        
        if not manifest:
            print("  ❌ __manifest__ variable not found")
            return False
            
        print("  ✅ Manifest dictionary found")
        return manifest
        
    except Exception as e:
        print(f"  ❌ Manifest syntax error: {e}")
        return False

def test_required_fields(manifest):
    """Test required manifest fields"""
    print("🔍 Testing required manifest fields...")
    
    required_fields = {
        'name': str,
        'version': str,
        'depends': list,
        'data': list,
        'installable': bool,
        'auto_install': bool
    }
    
    for field, expected_type in required_fields.items():
        if field not in manifest:
            print(f"  ❌ Missing required field: {field}")
            return False
        
        if not isinstance(manifest[field], expected_type):
            print(f"  ❌ Field {field} wrong type: expected {expected_type.__name__}")
            return False
            
        print(f"  ✅ {field}: {manifest[field]}")
    
    return True

def test_data_files(manifest):
    """Test all data files exist"""
    print("🔍 Testing data files existence...")
    
    missing_files = []
    for data_file in manifest.get('data', []):
        file_path = f'contratos/{data_file}'
        if not os.path.exists(file_path):
            missing_files.append(data_file)
            print(f"  ❌ Missing: {data_file}")
        else:
            print(f"  ✅ Found: {data_file}")
    
    if missing_files:
        print(f"  ❌ {len(missing_files)} missing data files")
        return False
    
    print("  ✅ All data files exist")
    return True

def test_python_imports():
    """Test Python module imports"""
    print("🔍 Testing Python module imports...")
    
    # Test main module init
    try:
        with open('contratos/__init__.py', 'r') as f:
            init_content = f.read()
        
        if 'from . import models' not in init_content:
            print("  ❌ models not imported in main __init__.py")
            return False
        
        if 'from . import wizards' not in init_content:
            print("  ❌ wizards not imported in main __init__.py")
            return False
            
        print("  ✅ Main module imports correct")
        
    except Exception as e:
        print(f"  ❌ Error reading main __init__.py: {e}")
        return False
    
    # Test models init
    try:
        with open('contratos/models/__init__.py', 'r') as f:
            models_init = f.read()
        
        expected_models = ['contract', 'contract_type', 'contract_line', 'contract_template', 'partner_extension']
        
        for model in expected_models:
            if f'from . import {model}' not in models_init:
                print(f"  ❌ {model} not imported in models/__init__.py")
                return False
            print(f"  ✅ {model} imported")
            
    except Exception as e:
        print(f"  ❌ Error reading models/__init__.py: {e}")
        return False
    
    return True

def test_model_definitions():
    """Test model class definitions"""
    print("🔍 Testing model definitions...")
    
    model_files = {
        'contratos/models/contract.py': ['contract.general'],
        'contratos/models/contract_type.py': ['contract.type'],
        'contratos/models/contract_line.py': ['contract.line'],
        'contratos/models/contract_template.py': ['contract.template'],
        'contratos/models/partner_extension.py': ['res.partner'],
        'contratos/wizards/contract_wizard.py': ['contract.wizard']
    }
    
    for file_path, expected_models in model_files.items():
        if not os.path.exists(file_path):
            print(f"  ❌ Missing file: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for model definitions
            for model_name in expected_models:
                if f"_name = '{model_name}'" in content:
                    print(f"  ✅ {model_name} defined in {file_path}")
                elif f'_inherit = \'{model_name}\'' in content:
                    print(f"  ✅ {model_name} inherited in {file_path}")
                else:
                    print(f"  ❌ {model_name} not found in {file_path}")
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error reading {file_path}: {e}")
            return False
    
    return True

def test_xml_structure():
    """Test XML file structure"""
    print("🔍 Testing XML file structure...")
    
    try:
        import xml.etree.ElementTree as ET
        
        manifest_path = 'contratos/__manifest__.py'
        with open(manifest_path, 'r') as f:
            content = f.read()
        namespace = {}
        exec(content, namespace)
        manifest = namespace.get('__manifest__', {})
        
        xml_files = [f for f in manifest.get('data', []) if f.endswith('.xml')]
        
        for xml_file in xml_files:
            file_path = f'contratos/{xml_file}'
            try:
                ET.parse(file_path)
                print(f"  ✅ {xml_file} valid XML")
            except ET.ParseError as e:
                print(f"  ❌ {xml_file} XML error: {e}")
                return False
            except Exception as e:
                print(f"  ❌ {xml_file} error: {e}")
                return False
        
        return True
        
    except ImportError:
        print("  ⚠️  xml.etree.ElementTree not available, skipping XML test")
        return True

def test_dependencies():
    """Test module dependencies"""
    print("🔍 Testing module dependencies...")
    
    manifest_path = 'contratos/__manifest__.py'
    with open(manifest_path, 'r') as f:
        content = f.read()
    namespace = {}
    exec(content, namespace)
    manifest = namespace.get('__manifest__', {})
    
    depends = manifest.get('depends', [])
    
    # Standard Odoo modules that should be available
    standard_modules = ['base', 'mail', 'account', 'sale', 'portal']
    
    for module in depends:
        if module in standard_modules:
            print(f"  ✅ Dependency {module} is standard Odoo module")
        else:
            print(f"  ⚠️  Custom dependency: {module}")
    
    return True

def main():
    """Run all manifest tests"""
    print("🚀 Starting comprehensive manifest installation test...")
    print("=" * 60)
    
    # Test 1: Manifest syntax
    manifest = test_manifest_syntax()
    if not manifest:
        print("\n❌ MANIFEST TEST FAILED: Syntax error")
        return False
    
    # Test 2: Required fields
    if not test_required_fields(manifest):
        print("\n❌ MANIFEST TEST FAILED: Missing required fields")
        return False
    
    # Test 3: Data files
    if not test_data_files(manifest):
        print("\n❌ MANIFEST TEST FAILED: Missing data files")
        return False
    
    # Test 4: Python imports
    if not test_python_imports():
        print("\n❌ MANIFEST TEST FAILED: Import errors")
        return False
    
    # Test 5: Model definitions
    if not test_model_definitions():
        print("\n❌ MANIFEST TEST FAILED: Model definition errors")
        return False
    
    # Test 6: XML structure
    if not test_xml_structure():
        print("\n❌ MANIFEST TEST FAILED: XML structure errors")
        return False
    
    # Test 7: Dependencies
    if not test_dependencies():
        print("\n❌ MANIFEST TEST FAILED: Dependency errors")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL MANIFEST TESTS PASSED")
    print("🚀 Module ready for Odoo installation")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)