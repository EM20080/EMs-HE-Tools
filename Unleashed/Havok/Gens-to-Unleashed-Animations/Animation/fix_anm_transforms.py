import os
import re
import subprocess

# Get the output folder path
output_folder = r"c:\Users\EM2008\Desktop\app src\HavokTest\HavokTest\bin\Debug\Animation\output"
havok_py = r"..\Havok.py"

# Get all anm.xml files
anm_files = [f for f in os.listdir(output_folder) if f.endswith('.anm.xml')]

def extract_first_transform(file_path, is_skeleton=False):
    """Extract the first transform (reference bone) from skeleton file"""
    with open(file_path, 'r', encoding='ascii') as f:
        content = f.read()
    
    # Find referencePose section and get first transform
    match = re.search(r'<hkparam name="referencePose" numelements="\d+">\s*\n\s*(\([^)]+\)\([^)]+\)\([^)]+\))', content)
    
    if match:
        return match.group(1)
    return None

def get_bone_count(skl_path):
    """Get the number of bones from skeleton file"""
    with open(skl_path, 'r', encoding='ascii') as f:
        content = f.read()
    
    match = re.search(r'<hkparam name="referencePose" numelements="(\d+)">', content)
    if match:
        return int(match.group(1))
    return None

def update_all_reference_bones(anm_path, skl_transform, bone_count):
    """Update ALL reference bone transforms across all frames in an animation file"""
    with open(anm_path, 'r', encoding='ascii') as f:
        lines = f.readlines()
    
    # Find the transforms section
    in_transforms = False
    transform_count = 0
    updated_count = 0
    
    for i, line in enumerate(lines):
        if '<hkparam name="transforms" numelements=' in line:
            in_transforms = True
            continue
        
        if in_transforms and '</hkparam>' in line:
            break
            
        if in_transforms:
            # Check if this line contains a transform (starts with whitespace and parenthesis)
            if line.strip().startswith('('):
                # Every bone_count transforms, we hit the reference bone
                if transform_count % bone_count == 0:
                    # This is a reference bone - replace it
                    indent = len(line) - len(line.lstrip())
                    lines[i] = ' ' * indent + skl_transform + '\n'
                    updated_count += 1
                transform_count += 1
    
    with open(anm_path, 'w', encoding='ascii') as f:
        f.writelines(lines)
    
    return updated_count

# Step 1: Check if animations need to be decompressed and convert them with Havok.py
print("Checking for spline compressed animations...")
for anm_file in anm_files:
    anm_path = os.path.join(output_folder, anm_file)
    
    # Check if this is a spline compressed animation
    with open(anm_path, 'r', encoding='ascii') as f:
        content = f.read()
    
    # If it has SplineSkeletalAnimation but no transforms, it needs conversion
    if 'hkaSplineSkeletalAnimation' in content and 'hkparam name="transforms"' not in content:
        print(f"  Converting {anm_file} from spline to interleaved format...")
        output_path = os.path.join(output_folder, anm_file.replace('.xml', '_550.xml'))
        
        # Run Havok.py to convert
        result = subprocess.run(['python', havok_py, anm_path, output_path], 
                              capture_output=True, text=True)
        
        if os.path.exists(output_path):
            # Replace original with converted
            os.remove(anm_path)
            os.rename(output_path, anm_path)
            print(f"    Converted successfully")
        else:
            print(f"    Warning: Failed to convert")

# Refresh the file list after conversion
anm_files = [f for f in os.listdir(output_folder) if f.endswith('.anm.xml')]

# Step 2: Process each animation file to fix reference bone positions
print("\nFixing reference bone positions...")
for anm_file in anm_files:
    # Get the base name to find corresponding skeleton file
    base_name = anm_file.replace('.anm.xml', '')
    skl_file = base_name + '.skl.xml'
    
    anm_path = os.path.join(output_folder, anm_file)
    skl_path = os.path.join(output_folder, skl_file)
    
    # Check if skeleton file exists
    if not os.path.exists(skl_path):
        print(f"Warning: Skeleton file not found for {anm_file}")
        continue
    
    # Extract reference bone transform from skeleton
    skl_transform = extract_first_transform(skl_path, is_skeleton=True)
    bone_count = get_bone_count(skl_path)
    
    if not skl_transform:
        print(f"Warning: Could not extract transform from {skl_file}")
        continue
    
    if not bone_count:
        print(f"Warning: Could not get bone count from {skl_file}")
        continue
    
    # Update ALL reference bone transforms in the animation file
    frames_updated = update_all_reference_bones(anm_path, skl_transform, bone_count)
    print(f"  Fixed {anm_file}: {frames_updated} frames updated (bone count: {bone_count})")

print("\nAll animations processed successfully!")
