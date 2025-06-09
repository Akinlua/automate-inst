#!/usr/bin/env python3
"""
Test script to verify Instagram Auto Poster setup
"""

import sys
import importlib
import subprocess
from pathlib import Path

def test_python_version():
    """Test Python version"""
    print("Testing Python version...")
    version = sys.version_info
    
    # Show current Python version
    print(f"Current Python: {version.major}.{version.minor}.{version.micro}")
    
    # Test if version meets requirements
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK (meets requirement: 3.8+)")
        
        # Also test what python commands are available
        import subprocess
        import shutil
        
        print("\nAvailable Python commands:")
        python_commands = ['python3.13', 'python3.12', 'python3.11', 'python3.10', 'python3.9', 'python3.8', 'python3', 'python']
        found_commands = []
        
        for cmd in python_commands:
            if shutil.which(cmd):
                try:
                    result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        version_str = result.stdout.strip() or result.stderr.strip()
                        found_commands.append(f"  {cmd}: {version_str}")
                except:
                    pass
        
        if found_commands:
            for cmd_info in found_commands:
                print(cmd_info)
        else:
            print("  No additional Python commands found")
            
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.8+")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\nTesting dependencies...")
    required_packages = [
        'selenium',
        'PIL',  # Pillow
        'dotenv',  # python-dotenv
        'schedule',
        'openai',
        'requests',
        'flask',
        'werkzeug',
        'pytz',
        'psutil',
        'undetected_chromedriver'
    ]
    
    all_good = True
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - MISSING")
            all_good = False
    
    return all_good

def test_files():
    """Test required files exist"""
    print("\nTesting required files...")
    required_files = [
        'app.py',
        'instagram_poster.py',
        'requirements.txt',
        'setup_integration.py',
        'vnc_setup.py',
        'run_scheduler.py'
    ]
    
    all_good = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} - OK")
        else:
            print(f"❌ {file} - MISSING")
            all_good = False
    
    return all_good

def test_directories():
    """Test required directories exist"""
    print("\nTesting directories...")
    required_dirs = [
        'templates',
        'static',
        'content'
    ]
    
    all_good = True
    for dir_name in required_dirs:
        if Path(dir_name).exists() and Path(dir_name).is_dir():
            print(f"✅ {dir_name}/ - OK")
        else:
            print(f"❌ {dir_name}/ - MISSING")
            all_good = False
    
    return all_good

def test_chrome():
    """Test Chrome installation"""
    print("\nTesting Chrome installation...")
    try:
        import undetected_chromedriver as uc
        print("✅ undetected_chromedriver - OK")
        
        # Try to create a Chrome options object
        options = uc.ChromeOptions()
        print("✅ Chrome options - OK")
        return True
    except Exception as e:
        print(f"❌ Chrome test failed: {e}")
        return False

def test_app_import():
    """Test if main app can be imported"""
    print("\nTesting app import...")
    try:
        from app import app
        print("✅ Flask app import - OK")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Instagram Auto Poster - Setup Verification")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies),
        ("Required Files", test_files),
        ("Directories", test_directories),
        ("Chrome Support", test_chrome),
        ("App Import", test_app_import)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Setup is ready.")
        print("You can now run: python app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("You may need to run the setup script again.")
    print("=" * 50)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 