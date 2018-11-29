# arxiv_scripts

For a folder directory like

* paper
  * imgs
    * a.png
    * b.png
  * figs
    * a.tex
  * main.tex
  
  Run the script as
  
  `python ./remove_unused_imgs.py --main_folder ./ --fig_folders ./figs --img_folders ./imgs`
  
  If `a.tex` only uses `a.png`, the remaining image, `b.png`, will be removed.
  
  Other optional arguments are
  
  ```
  -h, --help            show this help message and exit
  --main_folder MAIN_FOLDER
                        The top folder of the project
  --fig_folders FIG_FOLDERS [FIG_FOLDERS ...]
                        A list of folder where to find the text files
  --img_folders IMG_FOLDERS [IMG_FOLDERS ...]
                        A list of folders where the images are stored
  --dry_run             Does not edit or remove, only print changes
  --recursive           fig_folders and img_folders are searched recursively
  --replace_defs        Replace all \defs{} in the tex files with their values
  --remove_ext REMOVE_EXT [REMOVE_EXT ...]
                        Remove files with this extension, regardless if they
                        are being used
  --using_graphicspath  If set assumes that \graphicspath was used to include
                        files in img_folders subfolders of main_folder. For
                        this to work all folders added in img_folders must be
                        added to the \graphicspath```
