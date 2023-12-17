import json
import os
import subprocess
import re

def get_hostname():
    """Returns the hostname of the current server."""
    import socket
    return socket.gethostname()

def get_role(hostname, role_info_file):
    """Returns the role of the server with the given hostname."""
    with open(role_info_file, "r") as f:
        role_info = json.load(f)
        #print(role_info.items())
    for role, hostnames in role_info.items():
        if hostname in hostnames:
            return role
    return None

def get_mapping_info(mapping_file):
    """Returns the mapping information from the given mapping file."""
    with open(mapping_file, "r") as f:
        mapping = json.load(f)
        #print(mapping.items())
        return mapping

def sync_files(source_dir, destination_dir, rsync_options):
    """Synchronizes the files from the source directory to the destination directory using the given rsync options."""
    return subprocess.check_output(["rsync", rsync_options, source_dir+"/", destination_dir])

def delete_files(delete_info_file, source_dir, dest_dir, sub_dir):
    with open(delete_info_file, "r") as f:
        delete_info = json.load(f)
    deleted_files = []
    for role, files in delete_info.items():
        for filename in files:
            chef_workstation_file = os.path.join(source_dir, role, sub_dir, filename)
            destination_file = os.path.join(dest_dir, sub_dir, filename)

            if os.path.exists(chef_workstation_file):
                os.remove(chef_workstation_file)

            if os.path.exists(destination_file):
                deleted_files.append(filename)
                os.remove(destination_file)
                
    return deleted_files
        
def filter_rsync_output(rsync_output):
    """Filters lines from the rsync output that contain filenames and indents each line with a tab.

    Args:
        rsync_output: The rsync output.

    Returns:
        A list of filtered and indented lines.
    """
    rsync_output = rsync_output.decode('utf-8')
    # Replace all newline characters in the rsync_output_pc string with '\n'
    # Compile a regular expression to match newline characters
    newline_regex = re.compile(r'\n')
    rsync_output = newline_regex.sub(r'\n', rsync_output)
    filename_regex = re.compile(r'^[>|<|*]')
    filtered_lines = ["\t" + line for line in rsync_output.split('\n') if filename_regex.search(line)]
    indented_rsync_output = '\n'.join(filtered_lines)
    if not indented_rsync_output:
        return "\tNo files synced"
    return indented_rsync_output
    
def get_directory_permissions(directory_path):
    """
    Gets the mode, UID, and GID of a directory.

    Args:
        directory_path (str): The path to the directory.

    Returns:
        tuple: A tuple containing the mode, UID, and GID of the directory.
    """

    directory_stats = os.stat(directory_path)
    mode = directory_stats.st_mode
    uid = directory_stats.st_uid
    gid = directory_stats.st_gid

    return (mode, uid, gid)

def set_permissions_recursively(root_dir, mode, uid, gid):
    for root, dirs, files in os.walk(root_dir):
        os.chmod(root, mode)
        os.chown(root, uid, gid)

        for filename in files:
            filepath = os.path.join(root, filename)
            os.chmod(filepath, mode)
            os.chown(filepath, uid, gid)
            
def getTemplateRoles(template_file, mapping_role_file):
    mapping_role_info = get_mapping_info(mapping_role_file)
    return mapping_role_info.get(template_file)
    
def parse_template(template_file, role, mapping_file2):
    with open(template_file, 'r') as f:
        template_content = f.read()
    # Load JSON data
    with open(mapping_file2) as f:
      replacements = json.load(f)

    # Build replacement dict with formatted keys
    formatted_replacements = {f"<{key}>": value for key, value in replacements.items()}

    # Replace keys in template content
    for key, value in formatted_replacements.items():
        template_content = template_content.replace(key, value)
    parsed_content = ''
    role_specific_content = None
    content_roles = None
    in_role_section = False
    for line in template_content.splitlines():
        if line.startswith('<roles'):
            role_specific_content = ''
            in_role_section = True
            start_index = line.find("[")
            end_index = line.rfind("]")
            content_roles = line[start_index:end_index+1]
        elif line.startswith('<end>'):
            if role in content_roles:
                parsed_content += role_specific_content
            role_specific_content = None
            in_role_section = False
            content_roles = None
        elif in_role_section:
            role_specific_content += line + '\n'
        else:
            parsed_content += line + '\n'
    return parsed_content
    
def rsync_sync_directories(source_dir, target_dir, exclude_file, current_role, hostname, rsync_options):
  """
  Synchronizes two directories using rsync and deletes extra files in the target directory based on role-specific inclusions.

  Args:
    source_dir: Path to the source directory.
    target_dir: Path to the target directory.
    exclude_file: Path to the JSON file containing role-based exclusions.
  """

  # Read exclusion patterns from JSON file
  with open(exclude_file) as f:
    exclusions = json.load(f)

  # Build exclude options dynamically
  exclude_options = ""
  for filename, roles in exclusions.items():
    if current_role in roles:
      exclude_options += f"--exclude={filename} "
    elif hostname in roles:
      exclude_options += f"--exclude={filename} "
      

  # Combine options with source and target paths
  source_dir = source_dir + "/"
  rsync_command = f"rsync {rsync_options} {exclude_options} --delete  {source_dir} {target_dir}"

  # Execute rsync command with subprocess
  print(f"Running rsync command: {rsync_command}")
  return subprocess.check_output(rsync_command.split())

  print("Synchronization complete!")
  
def add_key_value_pair(json_file, value, key="my_key"):
  """
  Adds a key-value pair to a JSON file.

  Args:
    json_file: Path to the JSON file.
    value: The value to be added.
    key (optional): The key for the value (defaults to "my_key").
  """
  with open(json_file, "r+") as f:
    data = json.load(f)
    data.update({key: value})
    f.seek(0)
    json.dump(data, f, indent=4)
