import functions_and_dependencies as f
import logging
import os
import shutil
import datetime

base_dir = "/mnt/c/Users/mehul/OneDrive/Desktop/notepad-plus-dump"

#logging
now = datetime.datetime.now()
log_file_name = now.strftime("%Y-%m-%d_%H-%M-%S.log")
log_directory = os.path.join(base_dir, "apps/edp/chef_workstation/chef_logs")
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler(os.path.join(log_directory, log_file_name))
fh.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s\n")
fh.setFormatter(formatter)
logger.addHandler(fh)

#defining paths to relevant directories and files
source_dir = os.path.join(base_dir, "apps/edp/chef_workstation")
dest_dir = os.path.join(base_dir, "apps")
sub_dir = "edp"
delete_info_file=os.path.join(base_dir, "apps/edp/chef_workstation/delete_info.json")
role_info_file=os.path.join(base_dir, "apps/edp/chef_workstation/role_info.json")
mapping_info_file=os.path.join(base_dir, "apps/edp/chef_workstation/templates/mapping.json")

rsync_options = "-rlpgoDcvi"

#deleting files from delete_info.json
deleted_files = f.delete_files(delete_info_file, source_dir, dest_dir, sub_dir)
if not len(deleted_files) == 0:
    indented_filenames = ["\t" + filename for filename in deleted_files]
    indented_files_string = '\n'.join(indented_filenames)
    logger.info("Files deleted: \n%s", indented_files_string)

# Copy common sub_dir contents to destination sub_dir irrespective of the host
common_sub_dir = os.path.join(source_dir, "common", sub_dir)
dest_sub_dir = os.path.join(dest_dir, sub_dir)
rsync_output_common = f.sync_files(common_sub_dir, dest_sub_dir, rsync_options)
logger.info("rsync output common: \n%s", f.filter_rsync_output(rsync_output_common))

# Copy primary_coordinator sub_dir contents to destination sub_dir if the current host is part of the "primary_coordinator" role
primary_coordinator_dir = os.path.join(source_dir, "primary_coordinator", sub_dir)
hostname = f.get_hostname()
role = f.get_role(hostname, role_info_file)
if role == "primary_coordinator":
    rsync_output_pc = f.sync_files(primary_coordinator_dir, dest_sub_dir, rsync_options)
    logger.info("rsync output pc: \n%s", f.filter_rsync_output(rsync_output_pc))

# Copy secondary_coordinator sub_dir contents to destination sub_dir if the current host is part of the "secondary_coordinator" role
secondary_coordinator_dir = os.path.join(source_dir, "secondary_coordinator", sub_dir)
if role == "secondary_coordinator":
    rsync_output_sc = f.sync_files(secondary_coordinator_dir, dest_sub_dir, rsync_options)
    logger.info("rsync output sc: \n%s", f.filter_rsync_output(rsync_output_sc))
    
# Copy worker sub_dir contents to destination sub_dir if the current host is part of the "worker" role
worker_dir = os.path.join(source_dir, "worker", sub_dir)
if role == "worker":
    rsync_output_worker = f.sync_files(worker_dir, dest_sub_dir, rsync_options)
    logger.info("rsync output worker: \n%s", f.filter_rsync_output(rsync_output_worker))

# Process templates sub_dir contents
templates_dir = os.path.join(source_dir, "templates", sub_dir)
parsed_templates_dir = os.path.join(source_dir, "parsed_templates", sub_dir)
if not os.path.exists(parsed_templates_dir):
    os.makedirs(parsed_templates_dir)

for root, directories, files in os.walk(templates_dir):
    for directory in directories:
        relative_path = os.path.relpath(os.path.join(root, directory), templates_dir)
        parsed_dir_path = os.path.join(parsed_templates_dir, relative_path)
        if not os.path.exists(parsed_dir_path):
            os.makedirs(parsed_dir_path)
    for filename in files:
        relative_path = os.path.relpath(os.path.join(root, filename), templates_dir)
        source_template_file = os.path.join(templates_dir, relative_path)
        destination_file = os.path.join(parsed_templates_dir, relative_path)

        # Replace variables in the template file
        replaced_template_content = f.replace_variables(source_template_file, mapping_info_file, role_info_file)
        # Write the replaced template content to the destination file
        with open(destination_file, "w") as file:
            file.write(replaced_template_content)

# Sync the parsed template directory to the destination directory
rsync_output_templates = f.sync_files(parsed_templates_dir, dest_sub_dir, rsync_options)
logger.info("rsync output templates: \n%s", f.filter_rsync_output(rsync_output_templates))
shutil.rmtree(os.path.join(source_dir, "parsed_templates"))

