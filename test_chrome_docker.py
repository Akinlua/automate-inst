#!/usr/bin/env python3
"""
Chrome Driver Docker Diagnostic Tool
This script tests Chrome driver setup in Docker environment
"""

import os
import subprocess
import sys
from pathlib import Path

def print_colored(message, color_code):
    """Print colored output"""
    print(f"\033[{color_code}m{message}\033[0m")

def print_success(message):
    print_colored(f"✅ {message}", "92")

def print_error(message):
    print_colored(f"❌ {message}", "91")

def print_warning(message):
    print_colored(f"⚠️  {message}", "93")

def print_info(message):
    print_colored(f"ℹ️  {message}", "94")

def run_command(command, description):
    """Run a command and return result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out: {command}"
    except Exception as e:
        return False, "", str(e)

def check_chrome_installation():
    """Check Chrome installation"""
    print_info("Checking Chrome installation...")
    
    success, stdout, stderr = run_command("google-chrome --version", "Chrome version")
    if success:
        print_success(f"Chrome installed: {stdout.strip()}")
        return True
    else:
        print_error(f"Chrome not found: {stderr}")
        return False

def check_chromedriver_installation():
    """Check ChromeDriver installation"""
    print_info("Checking ChromeDriver installation...")
    
    success, stdout, stderr = run_command("chromedriver --version", "ChromeDriver version")
    if success:
        print_success(f"ChromeDriver installed: {stdout.strip()}")
        return True
    else:
        print_error(f"ChromeDriver not found: {stderr}")
        return False

def check_display_setup():
    """Check display setup for headless operation"""
    print_info("Checking display setup...")
    
    display = os.environ.get('DISPLAY', 'Not set')
    print_info(f"DISPLAY environment variable: {display}")
    
    # Check if Xvfb is running
    success, stdout, stderr = run_command("pgrep Xvfb", "Xvfb process")
    if success:
        print_success("Xvfb is running")
    else:
        print_warning("Xvfb not running - might be needed for GUI operations")
    
    return True

def check_chrome_permissions():
    """Check Chrome binary permissions"""
    print_info("Checking Chrome permissions...")
    
    chrome_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable", 
        "/opt/google/chrome/chrome"
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            stat = os.stat(path)
            print_success(f"Chrome found at {path} (permissions: {oct(stat.st_mode)})")
            return True
    
    print_error("Chrome binary not found in expected locations")
    return False

def test_basic_chrome_startup():
    """Test basic Chrome startup"""
    print_info("Testing basic Chrome startup...")
    
    chrome_cmd = """
    google-chrome --version > /dev/null 2>&1 && \
    google-chrome --no-sandbox --disable-dev-shm-usage --disable-gpu --headless --remote-debugging-port=9222 --disable-extensions about:blank &
    CHROME_PID=$!
    sleep 3
    kill $CHROME_PID 2>/dev/null
    wait $CHROME_PID 2>/dev/null
    echo "Chrome test completed"
    """
    
    success, stdout, stderr = run_command(chrome_cmd, "Chrome startup test")
    if success:
        print_success("Chrome basic startup test passed")
        return True
    else:
        print_error(f"Chrome startup failed: {stderr}")
        return False

def test_selenium_chrome():
    """Test Selenium with Chrome"""
    print_info("Testing Selenium Chrome setup...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')
        options.add_argument('--remote-debugging-port=9222')
        
        try:
            service = Service('/usr/local/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=options)
            driver.get("data:text/html,<html><body><h1>Test</h1></body></html>")
            title = driver.title
            driver.quit()
            print_success(f"Selenium Chrome test passed (page title: '{title}')")
            return True
        except Exception as e:
            print_error(f"Selenium Chrome test failed: {e}")
            return False
            
    except ImportError as e:
        print_error(f"Selenium not available: {e}")
        return False

def test_undetected_chrome():
    """Test undetected-chromedriver"""
    print_info("Testing undetected-chromedriver...")
    
    try:
        import undetected_chromedriver as uc
        
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')
        options.add_argument('--remote-debugging-port=9222')
        
        try:
            # Try with system chromedriver first
            driver = uc.Chrome(options=options, driver_executable_path='/usr/local/bin/chromedriver')
            driver.get("data:text/html,<html><body><h1>Test UC</h1></body></html>")
            title = driver.title
            driver.quit()
            print_success(f"Undetected Chrome test passed with system driver (page title: '{title}')")
            return True
        except Exception as e1:
            print_warning(f"System chromedriver failed: {e1}")
            try:
                # Try with auto-download
                driver = uc.Chrome(options=options)
                driver.get("data:text/html,<html><body><h1>Test UC Auto</h1></body></html>")
                title = driver.title
                driver.quit()
                print_success(f"Undetected Chrome test passed with auto-download (page title: '{title}')")
                return True
            except Exception as e2:
                print_error(f"Undetected Chrome test failed: {e2}")
                return False
            
    except ImportError as e:
        print_error(f"undetected-chromedriver not available: {e}")
        return False

def check_docker_resources():
    """Check Docker container resources"""
    print_info("Checking container resources...")
    
    # Check memory
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            for line in meminfo.split('\n'):
                if 'MemTotal:' in line:
                    mem_kb = int(line.split()[1])
                    mem_gb = mem_kb / 1024 / 1024
                    if mem_gb >= 2:
                        print_success(f"Memory: {mem_gb:.1f}GB (sufficient)")
                    else:
                        print_warning(f"Memory: {mem_gb:.1f}GB (might be low for Chrome)")
                    break
    except Exception as e:
        print_warning(f"Could not check memory: {e}")
    
    # Check /dev/shm
    success, stdout, stderr = run_command("df -h /dev/shm", "Shared memory check")
    if success:
        print_success(f"Shared memory: {stdout.strip()}")
    else:
        print_warning("Could not check /dev/shm")
    
    return True

def main():
    """Main diagnostic function"""
    print_colored("🔍 Chrome Driver Docker Diagnostic", "96")
    print_colored("=" * 50, "96")
    
    checks = [
        ("Chrome Installation", check_chrome_installation),
        ("ChromeDriver Installation", check_chromedriver_installation),
        ("Display Setup", check_display_setup),
        ("Chrome Permissions", check_chrome_permissions),
        ("Docker Resources", check_docker_resources),
        ("Basic Chrome Startup", test_basic_chrome_startup),
        ("Selenium Chrome", test_selenium_chrome),
        ("Undetected Chrome", test_undetected_chrome),
    ]
    
    results = []
    for name, check_func in checks:
        print_colored(f"\n📋 {name}", "95")
        print("-" * 30)
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Check failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print_colored("\n📊 Summary", "96")
    print("-" * 20)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<25} {status}")
    
    print_colored(f"\nOverall: {passed}/{total} checks passed", "92" if passed == total else "93")
    
    if passed < total:
        print_colored("\n💡 Troubleshooting Tips:", "94")
        print("- Restart the Docker container: docker-compose restart")
        print("- Rebuild the Docker image: docker-compose build --no-cache")
        print("- Check Docker logs: docker-compose logs -f")
        print("- Ensure sufficient memory allocation (>= 2GB)")
        print("- Try running with --privileged flag if needed")

if __name__ == "__main__":
    main() 