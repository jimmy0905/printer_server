# add poppler-24.02.0\Library\bin to PATH

import os
import subprocess

poppler_relative_path = 'poppler-24.02.0/Library/bin'
poppler_path = os.path.abspath(poppler_relative_path)

print(poppler_path)

# Get the current PATH variable
current_path = os.environ.get('PATH', '')

# Append the Poppler path to the current PATH variable
updated_path = f"{current_path};{poppler_path}"

# Update the PATH variable
os.environ['PATH'] = updated_path

# Now you can use the Poppler binaries in your script

# For example, you can run the `pdfinfo` command

subprocess.run(['pdfinfo', 'example.pdf'])