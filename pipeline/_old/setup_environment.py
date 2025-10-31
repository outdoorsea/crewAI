#!/usr/bin/env python3
"""
Environment setup script for Myndy AI Pipeline
Ensures all dependencies are available and creates a proper virtual environment if needed.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def create_virtual_environment():
    """Create a virtual environment in the pipeline directory"""
    venv_path = Path(__file__).parent / "venv"
    
    if venv_path.exists():
        print(f"✅ Virtual environment already exists at {venv_path}")
        return venv_path
    
    print(f"🔧 Creating virtual environment at {venv_path}")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print(f"✅ Virtual environment created successfully")
        return venv_path
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return None

def install_dependencies(venv_path=None):
    """Install required dependencies"""
    requirements = [
        'pydantic>=2.0.0',
        'fastapi>=0.104.0',
        'uvicorn>=0.24.0',
        'crewai>=0.28.0',
        'langchain>=0.1.0',
        'langchain-community>=0.0.20',
        'requests>=2.31.0',
        'python-dotenv>=1.0.0',
        'pyyaml>=6.0'
    ]
    
    if venv_path:
        # Use virtual environment pip
        if os.name == 'nt':  # Windows
            pip_path = venv_path / "Scripts" / "pip"
        else:  # Unix/Linux/macOS
            pip_path = venv_path / "bin" / "pip"
        pip_cmd = [str(pip_path)]
    else:
        # Use system pip with user flag
        pip_cmd = [sys.executable, "-m", "pip"]
    
    print(f"📦 Installing dependencies...")
    
    try:
        # Upgrade pip first
        upgrade_cmd = pip_cmd + ["install", "--upgrade", "pip"]
        if not venv_path:
            upgrade_cmd.append("--user")
        subprocess.run(upgrade_cmd, check=True)
        
        # Install requirements
        install_cmd = pip_cmd + ["install"] + requirements
        if not venv_path:
            install_cmd.append("--user")
        
        print(f"Running: {' '.join(install_cmd)}")
        result = subprocess.run(install_cmd, capture_output=True, text=True, check=True)
        print("✅ All dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False

def test_imports():
    """Test if all required packages can be imported"""
    packages = [
        'pydantic',
        'fastapi', 
        'uvicorn',
        'crewai',
        'langchain',
        'langchain_community',
        'requests',
        'dotenv',
        'yaml'
    ]
    
    print("🧪 Testing package imports...")
    failed_imports = []
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("\n🎉 All packages imported successfully!")
        return True

def create_activation_script():
    """Create a script to easily activate the environment and run the pipeline"""
    venv_path = Path(__file__).parent / "venv"
    
    if not venv_path.exists():
        return
    
    # Create activation script for Unix/Linux/macOS
    script_content = f"""#!/bin/bash
# Myndy AI Pipeline Activation Script

echo "🚀 Activating Myndy AI Pipeline Environment"
source "{venv_path}/bin/activate"

echo "✅ Environment activated"
echo "📍 Virtual environment: {venv_path}"
echo "🐍 Python: $(which python)"

echo ""
echo "Available commands:"
echo "  python myndy_ai_beta.py              # Run the beta pipeline"
echo "  python crewai_myndy_pipeline.py      # Run the main pipeline"
echo "  deactivate                           # Exit virtual environment"
echo ""
"""
    
    script_path = Path(__file__).parent / "activate_pipeline.sh"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make it executable
    os.chmod(script_path, 0o755)
    
    print(f"✅ Created activation script: {script_path}")
    print(f"Usage: source {script_path}")

def main():
    """Main setup process"""
    print("🔧 Myndy AI Pipeline Environment Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Try to create virtual environment
    venv_path = create_virtual_environment()
    
    # Install dependencies
    if venv_path:
        print("\n📦 Installing dependencies in virtual environment...")
        success = install_dependencies(venv_path)
    else:
        print("\n📦 Installing dependencies for user...")
        success = install_dependencies()
    
    if not success:
        print("\n❌ Setup failed - dependencies could not be installed")
        print("\nTry manual installation:")
        print("1. Create virtual environment: python3 -m venv venv")
        print("2. Activate it: source venv/bin/activate")
        print("3. Install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    
    # Test imports
    if venv_path:
        # Test in virtual environment
        python_path = venv_path / "bin" / "python"
        test_cmd = [str(python_path), "-c", "import pydantic, fastapi, crewai; print('All imports successful')"]
        try:
            subprocess.run(test_cmd, check=True)
            print("✅ Virtual environment imports working")
        except subprocess.CalledProcessError:
            print("❌ Virtual environment imports failed")
    else:
        if not test_imports():
            print("❌ Some imports failed")
            sys.exit(1)
    
    # Create activation script
    if venv_path:
        create_activation_script()
    
    print("\n🎉 Setup completed successfully!")
    
    if venv_path:
        print(f"\nTo use the pipeline:")
        print(f"1. Activate environment: source pipeline/activate_pipeline.sh")
        print(f"2. Run pipeline: python myndy_ai_beta.py")
    else:
        print(f"\nTo use the pipeline:")
        print(f"1. Navigate to pipeline directory: cd pipeline")
        print(f"2. Run pipeline: python myndy_ai_beta.py")

if __name__ == "__main__":
    main()