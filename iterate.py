import os
import re
import glob

# Define the replacement header code as a multi-line string.
replacement_code = """<header id="top">
		
		<div class="container">
			
			<div class="row">
				  
				<div class="col span_3">
					
					<a id="logo" href="./../">

						<img class="stnd default-logo dark-version" alt="CORE@SNU" src="./../wp-content/uploads/2018/11/l1.png" srcset="./../wp-content/uploads/2018/11/l1.png 1x, ./../wp-content/uploads/2018/11/l2.png 2x">
                        <img class="starting-logo default-logo" alt="CORE@SNU" src="./../wp-content/uploads/2018/11/l3.png" srcset="./../wp-content/uploads/2018/11/l3.png 1x, ./../wp-content/uploads/2018/11/l4.png 2x"> 

					</a>

				</div>
<!--/span_3-->
				
				<div class="col span_9 col_last">
					
						<!--mobile cart link-->
						<a id="mobile-cart-link" href="./../"><i class="icon-salient-cart"></i>
                        <div class="cart-wrap"><span>0 </span></div></a>
						<div class="slide-out-widget-area-toggle mobile-icon fullscreen-alt" data-icon-animation="simple-transform">
							<div>
                                <a href="#sidewidgetarea" class="closed">
                                    <span>
                                        <i class="lines-button x2">
                                            <i class="lines"></i>
                                        </i>
                                    </span>
                                </a>
                            </div> 
       					</div>
										
						<nav>
							<ul class="sf-menu">	
								<li id="menu-item-7116" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-home menu-item-7116">
                                    <a href="./../">Home</a>
                                </li>
								<li id="menu-item-7119" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children menu-item-7119">
								    <a href="./../current-members/">People</a>
                                    <ul class="sub-menu">
	                                    <li id="menu-item-7511" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-7511">
                                            <a href="./../current-members/">Current Members</a>
                                        </li>
	                                    <li id="menu-item-7117" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-7117">
                                            <a href="./../alumni/">Alumni</a>
                                        </li>
                                    </ul>
								</li>
								<li id="menu-item-7124" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-7124">
                                    <a href="./../publications/">Publications</a>
                                </li>
								<li id="menu-item-7128" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-7128">
                                    <a href="./../teaching/">Teaching</a>
                                </li>
								<li id="menu-item-7122" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-7122">
                                    <a href="./../news">News</a>
                                </li>
								<li id="menu-item-7118" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-7118">
                                    <a href="./../contact/">Contact</a>
                                </li>
							</ul>
						</nav>
				</div>"""

# Compile a regex pattern that matches content between the two markers.
# This uses positive lookbehind and lookahead so that the markers remain intact.
pattern = re.compile(r'(?<=<!--/search-outer-->).*?(?=<!--/span_9-->)', re.DOTALL)

# Get the absolute path of the folder where the Python file is located.
root_directory = os.path.abspath(".")

# Define the names of directories to exclude.
excluded_dirs = {"publications", "teaching", "news", "alumni", "current-members", "contact"}

# Recursively get all HTML files under the root directory.
html_files = glob.glob(os.path.join(root_directory, '**', '*.html'), recursive=True)

for filepath in html_files:
    file_dir = os.path.abspath(os.path.dirname(filepath))
    # Skip HTML files in the root folder (same folder as this Python file).
    if file_dir == root_directory:
        print(f"Skipping {filepath} (in root folder)")
        continue
    # Skip HTML files in any folder with a basename in the excluded list.
    if os.path.basename(file_dir) in excluded_dirs:
        print(f"Skipping {filepath} (in excluded folder)")
        continue

    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    # Only process the file if both markers exist.
    if re.search(pattern, content):
        new_content = re.sub(pattern, "\n" + replacement_code + "\n", content)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(new_content)
        print(f"Updated {filepath}")
    else:
        print(f"Markers not found in {filepath}")
