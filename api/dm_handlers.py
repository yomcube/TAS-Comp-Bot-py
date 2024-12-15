handlers_dict = {}
def add_dm_handler(comp, func):
    handlers_dict[comp] = func

def init_dm_handlers():
    from api.mkwii.mkwii_file_handling import handle_mkwii_files
    add_dm_handler("mkw", handle_mkwii_files)
    
    from api.nsmbwii.nsmbwii_file_handling import handle_nsmbwii_files
    add_dm_handler("nsmbw", handle_nsmbwii_files)
