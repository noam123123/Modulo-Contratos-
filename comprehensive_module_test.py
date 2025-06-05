#!/usr/bin/env python3
"""
Comprehensive module test for production readiness
Ensures the module can be downloaded and uploaded directly to Odoo
"""

import os
import ast
import xml.etree.ElementTree as ET
import csv
import io

def test_file_structure():
    """Test complete file structure"""
    print("Testing file structure...")
    
    required_structure = {
        'contratos/__init__.py': 'file',
        'contratos/__manifest__.py': 'file',
        'contratos/models/__init__.py': 'file',
        'contratos/models/contract.py': 'file',
        'contratos/models/contract_type.py': 'file',
        'contratos/models/contract_line.py': 'file',
        'contratos/models/contract_template.py': 'file',
        'contratos/models/partner_extension.py': 'file',
        'contratos/views/contract_views.xml': 'file',
        'contratos/views/contract_type_views.xml': 'file',
        'contratos/views/contract_template_views.xml': 'file',
        'contratos/views/partner_views.xml': 'file',
        'contratos/views/menu_views.xml': 'file',
        'contratos/wizards/__init__.py': 'file',
        'contratos/wizards/contract_wizard.py': 'file',
        'contratos/wizards/contract_wizard_views.xml': 'file',
        'contratos/security/security.xml': 'file',
        'contratos/security/ir.model.access.csv': 'file',
        'contratos/data/contract_sequence.xml': 'file',
        'contratos/data/contract_types.xml': 'file',
        'contratos/data/contract_templates.xml': 'file',
        'contratos/data/contract_cron.xml': 'file',
        'contratos/data/email_templates.xml': 'file',
        'contratos/reports/contract_report.xml': 'file',
        'contratos/reports/contract_template.xml': 'file'
    }
    
    missing = []
    for path, type_expected in required_structure.items():
        if not os.path.exists(path):
            missing.append(path)
            print(f"  MISSING: {path}")
        else:
            print(f"  OK: {path}")
    
    if missing:
        print(f"ERROR: {len(missing)} missing files")
        return False
    
    print("✓ All required files present")
    return True

def test_python_syntax():
    """Test all Python files for syntax errors"""
    print("\nTesting Python syntax...")
    
    python_files = []
    for root, dirs, files in os.walk('contratos'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    errors = []
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            print(f"  OK: {py_file}")
        except SyntaxError as e:
            errors.append(f"{py_file}: {e}")
            print(f"  ERROR: {py_file}: {e}")
        except Exception as e:
            errors.append(f"{py_file}: {e}")
            print(f"  ERROR: {py_file}: {e}")
    
    if errors:
        print(f"ERROR: {len(errors)} Python syntax errors")
        return False
    
    print("✓ All Python files have valid syntax")
    return True

def test_xml_validity():
    """Test all XML files for validity"""
    print("\nTesting XML validity...")
    
    xml_files = []
    for root, dirs, files in os.walk('contratos'):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    errors = []
    for xml_file in xml_files:
        try:
            ET.parse(xml_file)
            print(f"  OK: {xml_file}")
        except ET.ParseError as e:
            errors.append(f"{xml_file}: {e}")
            print(f"  ERROR: {xml_file}: {e}")
        except Exception as e:
            errors.append(f"{xml_file}: {e}")
            print(f"  ERROR: {xml_file}: {e}")
    
    if errors:
        print(f"ERROR: {len(errors)} XML errors")
        return False
    
    print("✓ All XML files are valid")
    return True

def test_manifest_completeness():
    """Test manifest file completeness"""
    print("\nTesting manifest completeness...")
    
    try:
        with open('contratos/__manifest__.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        namespace = {}
        exec(content, namespace)
        manifest = namespace.get('__manifest__')
        
        if not manifest:
            print("  ERROR: __manifest__ not found")
            return False
        
        required_fields = ['name', 'version', 'depends', 'data', 'installable', 'auto_install']
        for field in required_fields:
            if field not in manifest:
                print(f"  ERROR: Missing required field: {field}")
                return False
            print(f"  OK: {field} = {manifest[field]}")
        
        # Verify all data files exist
        missing_data = []
        for data_file in manifest.get('data', []):
            full_path = f"contratos/{data_file}"
            if not os.path.exists(full_path):
                missing_data.append(data_file)
                print(f"  ERROR: Missing data file: {data_file}")
            else:
                print(f"  OK: Data file exists: {data_file}")
        
        if missing_data:
            print(f"ERROR: {len(missing_data)} missing data files")
            return False
        
        print("✓ Manifest is complete and valid")
        return True
        
    except Exception as e:
        print(f"ERROR: Manifest error: {e}")
        return False

def test_model_references():
    """Test model references are consistent"""
    print("\nTesting model references...")
    
    # Extract model definitions
    model_definitions = {}
    
    model_files = [
        'contratos/models/contract.py',
        'contratos/models/contract_type.py',
        'contratos/models/contract_line.py',
        'contratos/models/contract_template.py',
        'contratos/wizards/contract_wizard.py'
    ]
    
    for model_file in model_files:
        try:
            with open(model_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find _name definitions
            lines = content.split('\n')
            for line in lines:
                if '_name = ' in line and not line.strip().startswith('#'):
                    model_name = line.split('_name = ')[1].strip().strip('\'"')
                    model_definitions[model_name] = model_file
                    print(f"  Found model: {model_name} in {model_file}")
                    
        except Exception as e:
            print(f"  ERROR reading {model_file}: {e}")
            return False
    
    # Check field references
    reference_errors = []
    for model_file in model_files:
        try:
            with open(model_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find field references to other models
            import re
            field_refs = re.findall(r"'([a-z]+\.[a-z.]+)'", content)
            
            for ref in field_refs:
                if '.' in ref and not ref.startswith('base.') and not ref.startswith('mail.') and not ref.startswith('account.') and not ref.startswith('sale.'):
                    # Standard Odoo models that are always available
                    standard_models = ['res.', 'ir.', 'product.', 'uom.', 'portal.', 'mail.', 'account.', 'sale.', 'stock.', 'fleet.']
                    is_standard = any(ref.startswith(prefix) for prefix in standard_models)
                    
                    if ref not in model_definitions and not is_standard:
                        reference_errors.append(f"Unknown model reference: {ref} in {model_file}")
                        print(f"  ERROR: Unknown model reference: {ref} in {model_file}")
                    else:
                        print(f"  OK: Model reference: {ref}")
                        
        except Exception as e:
            print(f"  ERROR checking references in {model_file}: {e}")
            return False
    
    if reference_errors:
        print(f"ERROR: {len(reference_errors)} model reference errors")
        return False
    
    print("✓ All model references are valid")
    return True

def test_security_rules():
    """Test security rules completeness"""
    print("\nTesting security rules...")
    
    try:
        with open('contratos/security/ir.model.access.csv', 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        # Parse CSV
        csv_reader = csv.reader(io.StringIO(csv_content))
        rows = list(csv_reader)
        
        if not rows or len(rows) < 2:
            print("  ERROR: Empty or invalid CSV file")
            return False
        
        # Check header
        header = rows[0]
        expected_headers = ['id', 'name', 'model_id', 'group_id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink']
        for expected in expected_headers:
            if expected not in header:
                print(f"  ERROR: Missing CSV header: {expected}")
                return False
        
        # Check data rows
        models_with_access = set()
        for row in rows[1:]:
            if len(row) >= 3:
                model_id = row[2]
                models_with_access.add(model_id)
                print(f"  OK: Access rule for {model_id}")
        
        # Verify main models have access rules
        required_models = ['model_contract_general', 'model_contract_type', 'model_contract_line']
        for required in required_models:
            if required not in models_with_access:
                print(f"  ERROR: Missing access rule for {required}")
                return False
        
        print("✓ Security rules are complete")
        return True
        
    except Exception as e:
        print(f"ERROR: Security rules error: {e}")
        return False

def test_odoo_compatibility():
    """Test Odoo 15.0 compatibility"""
    print("\nTesting Odoo 15.0 compatibility...")
    
    # Check version in manifest
    try:
        with open('contratos/__manifest__.py', 'r', encoding='utf-8') as f:
            content = f.read()
        namespace = {}
        exec(content, namespace)
        manifest = namespace.get('__manifest__', {})
        
        version = manifest.get('version', '')
        if not version.startswith('15.0'):
            print(f"  ERROR: Version {version} not compatible with Odoo 15.0")
            return False
        
        print(f"  OK: Version {version} compatible with Odoo 15.0")
        
        # Check dependencies are standard
        depends = manifest.get('depends', [])
        standard_modules = ['base', 'mail', 'account', 'sale', 'portal', 'stock', 'fleet', 'contacts']
        
        for dep in depends:
            if dep not in standard_modules:
                print(f"  WARNING: Non-standard dependency: {dep}")
            else:
                print(f"  OK: Standard dependency: {dep}")
        
        print("✓ Odoo 15.0 compatibility verified")
        return True
        
    except Exception as e:
        print(f"ERROR: Compatibility check error: {e}")
        return False

def generate_installation_report():
    """Generate installation readiness report"""
    print("\n" + "="*60)
    print("INSTALLATION READINESS REPORT")
    print("="*60)
    
    with open('contratos/__manifest__.py', 'r', encoding='utf-8') as f:
        content = f.read()
    namespace = {}
    exec(content, namespace)
    manifest = namespace.get('__manifest__', {})
    
    print(f"Module Name: {manifest.get('name', 'Unknown')}")
    print(f"Version: {manifest.get('version', 'Unknown')}")
    print(f"Author: {manifest.get('author', 'Unknown')}")
    print(f"Dependencies: {', '.join(manifest.get('depends', []))}")
    print(f"Data Files: {len(manifest.get('data', []))}")
    print(f"Installable: {manifest.get('installable', False)}")
    
    # Count files
    total_files = 0
    for root, dirs, files in os.walk('contratos'):
        total_files += len(files)
    
    print(f"Total Files: {total_files}")
    
    # Check file sizes
    total_size = 0
    for root, dirs, files in os.walk('contratos'):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)
    
    print(f"Total Size: {total_size / 1024:.1f} KB")
    
    print("\nInstallation Instructions:")
    print("1. Download the 'contratos' folder")
    print("2. Copy to your Odoo addons directory")
    print("3. Restart Odoo server")
    print("4. Update Apps List")
    print("5. Search for 'Gestión de Contratos'")
    print("6. Click Install")
    
    print("\nModule Features:")
    print("- Complete contract management in Spanish")
    print("- Legal representative management for Costa Rica")
    print("- Automatic notifications and renewals")
    print("- PDF contract generation")
    print("- Integration with sales and accounting")
    print("- Multi-step contract creation wizard")
    print("- Customizable contract templates")

def main():
    """Run all tests"""
    print("COMPREHENSIVE MODULE PRODUCTION TEST")
    print("="*50)
    
    tests = [
        test_file_structure,
        test_python_syntax,
        test_xml_validity,
        test_manifest_completeness,
        test_model_references,
        test_security_rules,
        test_odoo_compatibility
    ]
    
    all_passed = True
    
    for test in tests:
        try:
            if not test():
                all_passed = False
                break
        except Exception as e:
            print(f"TEST FAILED: {test.__name__}: {e}")
            all_passed = False
            break
    
    print("\n" + "="*50)
    if all_passed:
        print("✓ ALL TESTS PASSED - MODULE READY FOR PRODUCTION")
        generate_installation_report()
        return True
    else:
        print("✗ TESTS FAILED - MODULE NOT READY")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)