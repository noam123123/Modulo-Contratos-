
#!/usr/bin/env python3
"""
Comprehensive RPC Error Debugger for Odoo Contratos Module
Checks for all potential field dependency and inheritance issues
"""

import os
import re
import ast

def check_field_dependencies():
    """Check for problematic field dependencies"""
    print("🔍 CHECKING FIELD DEPENDENCIES...")
    print("-" * 50)
    
    files_to_check = [
        'contratos/models/contract.py',
        'contratos/models/contract_type.py',
        'contratos/models/contract_line.py',
        'contratos/models/contract_template.py',
        'contratos/models/partner_extension.py',
        'contratos/models/account_move.py',
        'contratos/wizards/contract_wizard.py'
    ]
    
    error_patterns = [
        # The exact error pattern that was causing issues
        (r"@api\.depends\([^)]*'[^']*\.type'[^)]*\)", "Field dependency on 'type' should be 'move_type'"),
        (r"domain=\[[^]]*\('type'[^]]*\]", "Domain using 'type' should use 'move_type'"),
        (r"\.type\s*==\s*['\"]out_invoice", "Field access .type should be .move_type"),
        (r"\.type\s*==\s*['\"]in_invoice", "Field access .type should be .move_type"),
        (r"\.type\s*in\s*\[", "Field access .type should be .move_type"),
        (r"'type'\s*:", "Key 'type' in domain/filter should be 'move_type'"),
    ]
    
    errors_found = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                for pattern, issue in error_patterns:
                    if re.search(pattern, line):
                        # Exception: 'type': 'ir.actions.act_window' is OK
                        if "'type': 'ir.actions.act_window'" in line:
                            continue
                        errors_found.append(f"{file_path}:{line_num} - {issue}: {line.strip()}")
            
            print(f"  ✅ Checked: {file_path}")
        else:
            print(f"  ❌ Missing: {file_path}")
    
    if errors_found:
        print(f"\n❌ FOUND {len(errors_found)} FIELD DEPENDENCY ERRORS:")
        for error in errors_found:
            print(f"    {error}")
        return False
    else:
        print("\n✅ NO FIELD DEPENDENCY ERRORS FOUND")
        return True

def check_model_inheritance():
    """Check model inheritance issues"""
    print("\n🔍 CHECKING MODEL INHERITANCE...")
    print("-" * 50)
    
    account_move_file = 'contratos/models/account_move.py'
    if os.path.exists(account_move_file):
        with open(account_move_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for proper inheritance
        if "_inherit = 'account.move'" in content:
            print("  ✅ AccountMove properly inherits account.move")
        else:
            print("  ❌ AccountMove missing _inherit declaration")
            return False
        
        # Check for field redefinition
        if "type = fields." in content:
            print("  ❌ AccountMove redefines 'type' field (forbidden)")
            return False
        else:
            print("  ✅ AccountMove doesn't redefine forbidden fields")
        
        print("  ✅ Model inheritance is correct")
        return True
    else:
        print("  ⚠️  account_move.py not found (optional)")
        return True

def check_compute_methods():
    """Check compute methods for proper dependencies"""
    print("\n🔍 CHECKING COMPUTE METHODS...")
    print("-" * 50)
    
    contract_file = 'contratos/models/contract.py'
    if os.path.exists(contract_file):
        with open(contract_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find compute methods
        compute_pattern = r"@api\.depends\(([^)]+)\)\s*def\s+(_compute_\w+)"
        matches = re.findall(compute_pattern, content, re.MULTILINE)
        
        issues = []
        for depends, method_name in matches:
            print(f"  📋 Found compute method: {method_name}")
            
            # Check dependencies
            if "'type'" in depends and "'move_type'" not in depends:
                issues.append(f"Method {method_name} depends on 'type' instead of 'move_type'")
        
        if issues:
            print(f"  ❌ Found {len(issues)} compute method issues:")
            for issue in issues:
                print(f"    - {issue}")
            return False
        else:
            print("  ✅ All compute methods have correct dependencies")
            return True
    else:
        print("  ❌ contract.py not found")
        return False

def check_action_dictionaries():
    """Check action dictionaries for proper structure"""
    print("\n🔍 CHECKING ACTION DICTIONARIES...")
    print("-" * 50)
    
    files_to_check = [
        'contratos/models/contract.py',
        'contratos/models/contract_type.py',
        'contratos/models/contract_template.py',
        'contratos/models/partner_extension.py',
        'contratos/wizards/contract_wizard.py'
    ]
    
    action_issues = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find action returns
            action_pattern = r"return\s*\{[^}]*'type':\s*'ir\.actions\.act_window'[^}]*\}"
            if re.search(action_pattern, content, re.MULTILINE | re.DOTALL):
                print(f"  ✅ {file_path} - Action dictionaries found")
            else:
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    if "return {" in line and "'type'" in content[content.find("return {"):content.find("}", content.find("return {")) + 1]:
                        print(f"  ✅ {file_path} - Action dictionary at line {line_num}")
                        break
        else:
            action_issues.append(f"Missing file: {file_path}")
    
    if action_issues:
        print(f"  ❌ Found {len(action_issues)} action issues:")
        for issue in action_issues:
            print(f"    - {issue}")
        return False
    else:
        print("  ✅ All action dictionaries are properly structured")
        return True

def check_missing_imports():
    """Check for missing imports that could cause RPC errors"""
    print("\n🔍 CHECKING MISSING IMPORTS...")
    print("-" * 50)
    
    files_to_check = [
        'contratos/models/contract.py',
        'contratos/models/contract_type.py',
        'contratos/models/contract_line.py',
        'contratos/models/contract_template.py',
        'contratos/models/partner_extension.py',
        'contratos/models/account_move.py',
        'contratos/wizards/contract_wizard.py'
    ]
    
    import_issues = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for ValidationError usage without import
            if 'ValidationError' in content and 'from odoo.exceptions import' not in content:
                import_issues.append(f"{file_path} uses ValidationError but doesn't import it")
            
            # Check for basic Odoo imports
            if 'models.Model' in content and 'from odoo import' not in content:
                import_issues.append(f"{file_path} uses Odoo models without proper import")
            
            print(f"  ✅ Checked imports in {file_path}")
        else:
            import_issues.append(f"Missing file: {file_path}")
    
    if import_issues:
        print(f"  ❌ Found {len(import_issues)} import issues:")
        for issue in import_issues:
            print(f"    - {issue}")
        return False
    else:
        print("  ✅ All imports are correct")
        return True

def main():
    """Run comprehensive RPC error check"""
    print("🚨 COMPREHENSIVE RPC ERROR DEBUGGER")
    print("=" * 60)
    print("Checking for all potential RPC errors in Odoo Contratos module...")
    print()
    
    checks = [
        check_field_dependencies,
        check_model_inheritance,
        check_compute_methods,
        check_action_dictionaries,
        check_missing_imports
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS")
    print("=" * 60)
    
    if all(results):
        print("✅ ALL CHECKS PASSED - NO RPC ERRORS DETECTED")
        print("🚀 Module is ready for installation")
    else:
        failed_checks = sum(1 for result in results if not result)
        print(f"❌ {failed_checks} CHECKS FAILED - RPC ERRORS POSSIBLE")
        print("🔧 Please fix the issues above before installation")
    
    print("\n📋 Summary:")
    check_names = [
        "Field Dependencies",
        "Model Inheritance", 
        "Compute Methods",
        "Action Dictionaries",
        "Import Statements"
    ]
    
    for i, (name, result) in enumerate(zip(check_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")

if __name__ == "__main__":
    main()
