#!/usr/bin/env python3
"""
Package plugin for distribution
"""
import zipfile
import os
from pathlib import Path

def create_package():
    package_files = [
        '../share_to_s3.py',
        '../Main.sublime-menu',
        '../Default.sublime-commands',
        '../ShareToS3.sublime-settings'
    ]
    
    # Create output directory
    output_dir = Path('../dist')
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / 'ShareToS3.sublime-package'
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as pkg:
        for file in package_files:
            if os.path.exists(file):
                pkg.write(file)
                print(f"Added: {file}")
            else:
                print(f"Warning: {file} not found")
    
    print(f"Package created: {output_path}")

if __name__ == '__main__':
    create_package()