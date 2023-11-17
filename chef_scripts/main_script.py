import functions_and_dependencies as f
import logging
import os
import shutil
import datetime

base_dir = "/mnt/c/Users/mehul/OneDrive/Desktop/notepad-plus-dump"

#defining paths to relevant directories and files
source_dir = os.path.join(base_dir, "apps/edp/chef_workstation")
mode, uid, gid = f.get_directory_permissions(source_dir)
dest_dir = os.path.join(base_dir, "apps")
sub_dir = "edp"
delete_info_file=os.path.join(base_dir, "apps/edp/chef_workstation/delete_info.json")
role_info_file=os.path.join(base_dir, "apps/edp/chef_workstation/role_info.json")
mapping_info_file=os.path.join(base_dir, "apps/edp/chef_workstation/templates/mapping.json")

#logging
now = datetime.datetime.now()
log_file_name = now.strftime("%Y-%m-%d_%H-%M-%S.log")
log_directory = os.path.join(base_dir, "apps/edp/chef_workstation/chef_logs")
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
    # Set the permissions and ownership of the log directory
    os.chmod(log_directory, mode)
    os.chown(log_directory, uid, gid)
    
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = os.path.join(log_directory, log_file_name)
with open(log_file, 'w') as lf:
    pass 
os.chmod(log_file, mode)
os.chown(log_file, uid, gid)
fh = logging.FileHandler(log_file)
fh.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s\n")
fh.setFormatter(formatter)
logger.addHandler(fh)

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
if os.path.exists(parsed_templates_dir):
    shutil.rmtree(parsed_templates_dir)
shutil.copytree(templates_dir, parsed_templates_dir)

for root, directories, files in os.walk(parsed_templates_dir):
    for filename in files:
        template_file = os.path.join(root, filename)

        # Replace variables in the template file
        replaced_template_content = f.replace_variables(template_file, mapping_info_file, role_info_file)
        # Write the replaced template content to the destination file
        with open(template_file, "w") as file:
            file.write(replaced_template_content)
f.set_permissions_recursively(os.path.join(source_dir, "parsed_templates"), mode, uid, gid)
# Sync the parsed template directory to the destination directory
rsync_output_templates = f.sync_files(parsed_templates_dir, dest_sub_dir, rsync_options)
logger.info("rsync output templates: \n%s", f.filter_rsync_output(rsync_output_templates))
#shutil.rmtree(os.path.join(source_dir, "parsed_templates"))

