#!/usr/bin/env python3
"""
VNC Functionality Test Script
Tests VNC setup and integration with Instagram Auto Poster
"""

import os
import sys
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test if VNC modules can be imported"""
    logger.info("Testing VNC module imports...")
    
    try:
        from vnc_setup import start_vnc_chrome_session, get_vnc_status, get_vnc_access_info, stop_vnc_session
        logger.info("✓ VNC modules imported successfully")
        return True
    except ImportError as e:
        logger.error(f"✗ Failed to import VNC modules: {e}")
        return False

def test_system_compatibility():
    """Test system compatibility for VNC"""
    logger.info("Testing system compatibility...")
    
    try:
        from vnc_setup import vnc_manager
        compatible = vnc_manager.check_system_compatibility()
        
        if compatible:
            logger.info("✓ System is compatible with VNC")
        else:
            logger.error("✗ System is not compatible with VNC")
            
        return compatible
    except Exception as e:
        logger.error(f"✗ Error checking compatibility: {e}")
        return False

def test_vnc_dependencies():
    """Test if VNC dependencies are installed"""
    logger.info("Testing VNC dependencies...")
    
    dependencies = {
        'vncserver': ['vncserver', 'tightvncserver'],
        'websockify': ['websockify'],
        'chrome': ['google-chrome', 'chromium-browser', 'chromium'],
        'fluxbox': ['fluxbox'],
        'xterm': ['xterm']
    }
    
    results = {}
    for dep_name, commands in dependencies.items():
        found = False
        for cmd in commands:
            if os.system(f"which {cmd} > /dev/null 2>&1") == 0:
                logger.info(f"✓ {dep_name} found: {cmd}")
                found = True
                break
        
        if not found:
            logger.warning(f"✗ {dep_name} not found (tried: {', '.join(commands)})")
        
        results[dep_name] = found
    
    return results

def test_api_endpoints():
    """Test VNC API endpoints"""
    logger.info("Testing VNC API endpoints...")
    
    try:
        import requests
        
        # Test VNC check endpoint
        response = requests.get('http://localhost:5002/api/vnc/check')
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✓ VNC check endpoint working: {data.get('vnc_available', False)}")
            return True
        else:
            logger.error(f"✗ VNC check endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.warning("✗ Cannot test API endpoints - Flask app not running")
        return False
    except ImportError:
        logger.warning("✗ Requests module not available for API testing")
        return False
    except Exception as e:
        logger.error(f"✗ Error testing API endpoints: {e}")
        return False

def test_vnc_startup_simulation():
    """Simulate VNC startup without actually starting services"""
    logger.info("Testing VNC startup simulation...")
    
    try:
        from vnc_setup import VNCServerManager
        
        vnc = VNCServerManager()
        
        # Test configuration
        logger.info(f"VNC Display: {vnc.vnc_display}")
        logger.info(f"VNC Port: {vnc.vnc_port}")
        logger.info(f"Web Port: {vnc.vnc_web_port}")
        
        # Test VNC directory creation
        vnc.vnc_dir.mkdir(exist_ok=True, mode=0o700)
        logger.info(f"✓ VNC directory created: {vnc.vnc_dir}")
        
        # Test status checking (without actual processes)
        status = vnc.get_status()
        logger.info(f"✓ Status check working: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ VNC startup simulation failed: {e}")
        return False

def test_chrome_profile():
    """Test Chrome profile setup"""
    logger.info("Testing Chrome profile setup...")
    
    profile_path = Path("chrome_profile_instagram")
    
    try:
        # Check if profile exists
        if profile_path.exists():
            logger.info(f"✓ Chrome profile exists: {profile_path}")
            logger.info(f"Profile size: {sum(f.stat().st_size for f in profile_path.rglob('*') if f.is_file()) // 1024} KB")
        else:
            logger.info(f"Profile doesn't exist yet: {profile_path}")
            
        # Check write permissions
        test_file = profile_path / "test_write.tmp"
        try:
            profile_path.mkdir(exist_ok=True)
            test_file.write_text("test")
            test_file.unlink()
            logger.info("✓ Chrome profile directory is writable")
        except Exception as e:
            logger.error(f"✗ Chrome profile directory not writable: {e}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"✗ Chrome profile test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all VNC tests"""
    logger.info("=" * 60)
    logger.info("VNC COMPREHENSIVE TEST SUITE")
    logger.info("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("System Compatibility", test_system_compatibility),
        ("Dependencies Check", test_vnc_dependencies),
        ("API Endpoints", test_api_endpoints),
        ("VNC Startup Simulation", test_vnc_startup_simulation),
        ("Chrome Profile", test_chrome_profile)
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! VNC setup is ready.")
    elif passed >= total * 0.7:  # 70% pass rate
        logger.warning("⚠️  Most tests passed. Some optional features may not work.")
    else:
        logger.error("❌ Many tests failed. VNC setup needs attention.")
    
    # Recommendations
    logger.info("\n📋 RECOMMENDATIONS:")
    
    if not results.get("Dependencies Check", False):
        logger.info("1. Run: sudo bash install_vnc.sh")
    
    if not results.get("API Endpoints", False):
        logger.info("2. Start Flask app: python3 app.py")
    
    if not results.get("System Compatibility", False):
        logger.info("3. VNC only works on Linux systems")
    
    logger.info("4. Check VNC_SETUP_README.md for detailed setup instructions")
    
    return passed >= total * 0.7

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 