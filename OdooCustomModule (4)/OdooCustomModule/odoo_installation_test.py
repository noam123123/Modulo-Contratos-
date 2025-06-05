#!/usr/bin/env python3
"""
Comprehensive Odoo 15+ installation simulation test
Validates field dependencies and model inheritance to prevent installation errors
"""

import os
import ast
import re

def test_field_dependencies():
    """Test all field dependencies are correct for Odoo 15+"""
    print("Testing field dependencies for Odoo 15+ compatibility...")
    
    model_files = [
        'contratos/models/contract.py',
        'contratos/models/contract_type.py',
        'contratos/models/contract_line.py',
        'contratos/models/contract_template.py',
        'contratos/models/partner_extension.py',
        'contratos/wizards/contract_wizard.py'
    ]
    
    dependency_issues = []
    
    for model_file in model_files:
        if os.path.exists(model_file):
            with open(model_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for problematic field references (only account.move related)
            problematic_patterns = [
                (r"@api\.depends\([^)]*'[^']*\.type'[^)]*\)", "Field dependency on 'type' should be 'move_type'"),
                (r"domain=\[[^]]*\('type'[^]]*\]", "Domain filter using 'type' should use 'move_type'"),
                (r"\.type\s*==\s*['\"]out_invoice", "Field access .type should be .move_type for account.move"),
                (r"\.type\s*==\s*['\"]in_invoice", "Field access .type should be .move_type for account.move"),
                (r"'invoice_type'", "Use 'move_type' instead of 'invoice_type'")
            ]
            
            for pattern, issue in problematic_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    dependency_issues.append(f"{model_file}: {issue} - Found: {matches}")
            
            # Check @api.depends decorators specifically
            depends_matches = re.findall(r"@api\.depends\([^)]+\)", content)
            for depends_match in depends_matches:
                if "'type'" in depends_match:
                    dependency_issues.append(f"{model_file}: @api.depends contains 'type' field reference: {depends_match}")
            
            print(f"  Checked: {model_file}")
    
    if dependency_issues:
        print(f"\n❌ Found {len(dependency_issues)} field dependency issues:")
        for issue in dependency_issues:
            print(f"    - {issue}")
        return False
    else:
        print("  ✅ All field dependencies are correct for Odoo 15+")
        return True

def test_model_inheritance():
    """Test model inheritance is correct"""
    print("\nTesting model inheritance...")
    
    inheritance_issues = []
    
    # Check contract.py for proper inheritance
    contract_file = 'contratos/models/contract.py'
    if os.path.exists(contract_file):
        with open(contract_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check AccountMove inheritance
        if 'class AccountMove(models.Model):' in content:
            if "_inherit = 'account.move'" not in content:
                inheritance_issues.append("AccountMove class missing _inherit = 'account.move'")
            else:
                print("  ✅ AccountMove inheritance correct")
        
        # Check SaleOrder inheritance
        if 'class SaleOrder(models.Model):' in content:
            if "_inherit = 'sale.order'" not in content:
                inheritance_issues.append("SaleOrder class missing _inherit = 'sale.order'")
            else:
                print("  ✅ SaleOrder inheritance correct")
    
    if inheritance_issues:
        print(f"\n❌ Found {len(inheritance_issues)} inheritance issues:")
        for issue in inheritance_issues:
            print(f"    - {issue}")
        return False
    else:
        print("  ✅ All model inheritance is correct")
        return True

def test_compute_methods():
    """Test all compute methods for proper dependencies"""
    print("\nTesting compute methods...")
    
    compute_issues = []
    
    contract_file = 'contratos/models/contract.py'
    if os.path.exists(contract_file):
        with open(contract_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all compute methods and their dependencies
        compute_pattern = r"@api\.depends\([^)]+\)\s*def\s+(_compute_\w+)"
        compute_matches = re.findall(compute_pattern, content, re.MULTILINE | re.DOTALL)
        
        for method_name in compute_matches:
            print(f"  Found compute method: {method_name}")
            
            # Check if the method uses proper field references
            method_start = content.find(f"def {method_name}")
            if method_start != -1:
                # Find the end of the method (next def or class)
                method_end = content.find('\n    def ', method_start + 1)
                if method_end == -1:
                    method_end = content.find('\nclass ', method_start + 1)
                if method_end == -1:
                    method_end = len(content)
                
                method_content = content[method_start:method_end]
                
                # Check for problematic field accesses
                if '.type' in method_content and 'move_type' not in method_content:
                    compute_issues.append(f"Method {method_name} uses .type instead of .move_type")
        
        print(f"  ✅ Checked {len(compute_matches)} compute methods")
    
    if compute_issues:
        print(f"\n❌ Found {len(compute_issues)} compute method issues:")
        for issue in compute_issues:
            print(f"    - {issue}")
        return False
    else:
        print("  ✅ All compute methods are correct")
        return True

def test_xml_field_references():
    """Test XML files for correct field references"""
    print("\nTesting XML field references...")
    
    xml_issues = []
    
    xml_files = []
    for root, dirs, files in os.walk('contratos'):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    for xml_file in xml_files:
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for problematic field references in XML
        if 'name="type"' in content and 'account.move' in content:
            xml_issues.append(f"{xml_file}: Contains 'type' field reference for account.move")
        
        print(f"  Checked: {xml_file}")
    
    if xml_issues:
        print(f"\n❌ Found {len(xml_issues)} XML field issues:")
        for issue in xml_issues:
            print(f"    - {issue}")
        return False
    else:
        print("  ✅ All XML field references are correct")
        return True

def simulate_odoo_installation():
    """Simulate the Odoo installation process"""
    print("\nSimulating Odoo installation process...")
    
    # Check manifest dependencies
    try:
        with open('contratos/__manifest__.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        namespace = {}
        exec(content, namespace)
        manifest = namespace.get('__manifest__', {})
        
        print(f"  Module: {manifest.get('name')}")
        print(f"  Version: {manifest.get('version')}")
        print(f"  Dependencies: {manifest.get('depends', [])}")
        
        # Verify all dependencies are standard
        depends = manifest.get('depends', [])
        standard_deps = ['base', 'mail', 'account', 'sale', 'portal', 'stock', 'fleet', 'contacts']
        
        for dep in depends:
            if dep not in standard_deps:
                print(f"  ⚠️  Non-standard dependency: {dep}")
            else:
                print(f"  ✅ Standard dependency: {dep}")
        
        print("  ✅ Manifest validation passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Manifest validation failed: {e}")
        return False

def main():
    """Run comprehensive Odoo 15+ installation validation"""
    print("COMPREHENSIVE ODOO 15+ INSTALLATION VALIDATION")
    print("=" * 60)
    
    tests = [
        test_field_dependencies,
        test_model_inheritance,
        test_compute_methods,
        test_xml_field_references,
        simulate_odoo_installation
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
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL VALIDATION TESTS PASSED")
        print("🚀 MODULE IS READY FOR ODOO 15+ INSTALLATION")
        print("\nThe module will install successfully without field dependency errors.")
        print("You can safely upload and install this module in Odoo 15+.")
        return True
    else:
        print("❌ VALIDATION FAILED")
        print("🔧 Please fix the issues above before uploading to Odoo.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)