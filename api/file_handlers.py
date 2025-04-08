from api.mkwii.mkwii_file_handling import handle_mkwii_files
from api.nsmbwii.nsmbwii_file_handling import handle_nsmbwii_files

handlers_dict = {}
def add_file_handler(comp, func):
    handlers_dict[comp] = func

def init_file_handlers():
    add_file_handler("mkw", handle_mkwii_files)
    add_file_handler("nsmbw", handle_nsmbwii_files)
