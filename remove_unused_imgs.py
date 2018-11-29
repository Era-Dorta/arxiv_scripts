import glob
import os
import re
import argparse


def main(args):
    # List of *.tex files in fig_folders
    tex_files = get_tex_file_list(fig_folders=args.fig_folders, recursive=args.recursive)

    if args.replace_defs:
        replace_defs(tex_files=tex_files, dry_run=args.dry_run)
        #return  # Do one task at a time

    # List of image paths in img_folders
    img_files = get_img_file_list(img_folders=args.img_folders, recursive=args.recursive)

    # Create a dictionary with all the image paths that are used in the tex files
    used_img_paths = find_used_imgs(main_folder=args.main_folder, tex_files=tex_files, img_folders=args.img_folders,
                                    using_graphicspath=args.using_graphicspath)

    # Remove all the images that are not used
    remove_used_images(img_files=img_files, main_folder=args.main_folder, used_img_paths=used_img_paths,
                       remove_ext=args.remove_ext, dry_run=args.dry_run)


def get_graphicspath_replace_dict(main_folder, img_folders):
    # Dictionary with the missing paths due to using \graphicspath{{folder},...}
    img_sub_folder_replace = dict()
    for img_folder in img_folders:
        img_folder_base_long = img_folder.replace(main_folder, '')  # Folder name without main_folder

        if img_folder_base_long[0] == os.sep:  # Remove the / at the start
            img_folder_base_long = img_folder_base_long[1:]

        # dict contains the last folder name and full folder name without main_folder
        img_folder_base_short = os.path.basename(img_folder)
        img_sub_folder_replace[img_folder_base_short] = img_folder_base_long

    return img_sub_folder_replace


def get_img_file_list(img_folders, recursive):
    # List of image paths in img_folders
    img_files = []
    for img_folder in img_folders:
        img_files += glob.glob(os.path.join(img_folder, '**', '*'), recursive=recursive)
    return img_files


def get_tex_file_list(fig_folders, recursive):
    # List of *.tex files in fig_folders
    tex_files = []
    for fig_folder in fig_folders:
        tex_files += glob.glob(os.path.join(fig_folder, '**', '*.tex'), recursive=recursive)
    return tex_files


def remove_used_images(img_files, main_folder, used_img_paths, remove_ext, dry_run):
    # Remove all the images that are not in used_img_paths
    num_remove = 0
    for img_path in img_files:
        if not os.path.isdir(img_path):  # Path is not a folder
            base_img_path = img_path.replace(main_folder, '')  # Remove the main dir
            if base_img_path[0] == os.sep:  # Remove the / at the start
                base_img_path = base_img_path[1:]
            img_path_no_ext, img_path_ext = base_img_path.split('.')  # remove the extension name
            if used_img_paths.get(img_path_no_ext) is None or img_path_ext in remove_ext:
                print('Remove: ' + img_path)
                if not dry_run:
                    os.remove(img_path)
                num_remove += 1
            else:
                print('Keep ' + img_path)
                pass
    print('Removed {}/{} images'.format(num_remove, len(img_files)))


def find_used_imgs(main_folder, tex_files, img_folders, using_graphicspath):
    # Dictionary with the missing paths due to using \graphicspath{{folder},...}
    img_sub_folder_replace = get_graphicspath_replace_dict(main_folder=main_folder, img_folders=img_folders)

    match_string = r'\\includegraphics\[.*\]{(.+?)}'
    match_ob = re.compile(match_string)

    # Create match objects for short_folder name in the start of [*]
    match_obj_sub_folder = dict()
    for short_name, long_name in img_sub_folder_replace.items():
        match_obj_sub_folder[long_name] = re.compile('^' + short_name + '*')

    used_img_paths = dict()
    for tex_file in tex_files:
        with open(tex_file, 'r') as f:
            for line in f:
                match = match_ob.search(line)
                if match:
                    img_path = match.group(1)
                    if using_graphicspath:
                        # Add the full paths that were missing due to \graphicspath
                        for long_name, sub_folder_match in match_obj_sub_folder.items():
                            img_path = sub_folder_match.sub(long_name, img_path)

                    used_img_paths[img_path] = True
    return used_img_paths


def replace_defs(tex_files, dry_run):
    # Replace the values for \def\*{*} in the tex files
    match_string = r'\\def\\(.+?){(.+?)}'
    match_ob = re.compile(match_string)
    for tex_file in tex_files:
        if dry_run:
            print('File ' + tex_file)
        file_content = []
        with open(tex_file, 'r') as f:
            name_defs = dict()
            for line in f:
                match = match_ob.search(line)
                if match:
                    # Found a \def\*{*} definition in this line, store its values
                    name_def = '\\' + match.group(1)  # the \def*
                    replace_str = match.group(2)  # the value inside the {*}
                    name_defs[name_def] = replace_str
                else:
                    original_line = line
                    # No \def\*{*} definition in this line, try replacing with all known \def\*{*}
                    for name_def, replace_str in name_defs.items():
                        line = line.replace(name_def, replace_str)

                    if original_line != line:
                        # Print the replacement
                        print('\t- ' + original_line.rstrip("\n\r"))
                        print('\t+ ' + line.rstrip("\n\r") + '\n')

                file_content.append(line)

        # Rewrite the file with the replaced definitions
        if not dry_run:
            with open(tex_file, 'w') as f:
                for line in file_content:
                    f.write(line)
            print('Updated file ' + tex_file)

        print('')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--main_folder", help="The top folder of the project")
    parser.add_argument("--fig_folders", help="A list of folder where to find the text files", nargs='+', default=[])
    parser.add_argument("--img_folders", help="A list of folders where the images are stored", nargs='+', default=[])
    parser.add_argument("--dry_run", help="Does not edit or remove, only print changes", action='store_true')
    parser.add_argument("--recursive", help="fig_folders and img_folders are searched recursively", action='store_true')
    parser.add_argument("--replace_defs", help="Replace all \\defs{} in the tex files with their values",
                        action='store_true')
    parser.add_argument("--remove_ext", help="Remove files with this extension, regardless if they are being used",
                        nargs='+', default=['svg'])
    parser.add_argument("--using_graphicspath", action='store_true',
                        help="""If set assumes that \\graphicspath was used to include files in
                              img_folders subfolders of main_folder. For this to work all folders
                              added in img_folders must be added to the \\graphicspath""")
    args = parser.parse_args()

    if args.main_folder is None:
        raise ValueError("Missing argument --main_folder")
    if args.img_folders is []:
        raise ValueError("Missing argument --img_folders")
    if args.fig_folders is []:
        raise ValueError("Missing argument --fig_folders")

    main(args)
