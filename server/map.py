import networkx as nx
import osmnx as ox
import requests
import matplotlib.cm as cm
import matplotlib.colors as colors
from matplotlib.patches import Patch
from matplotlib.pyplot import scatter, close
from matplotlib.lines import Line2D

# To add text and a border to the map
from PIL import Image, ImageOps, ImageColor, ImageFont, ImageDraw 

BACKGROUND = "#211717"
CEMETERY = "#f58b54"
color_map = {
    'long_road': "#dfddc7",
    "medium_long_road": "#dfddc7",
    "medium_road": "#dfddc7",
    "medium_short_road": BACKGROUND,
    "short_road": BACKGROUND,
    "default": "#dfddc7"
}

thickness_map = [['footway', '']]

def _color(color, mode):
    color = ImageColor.getcolor(color, mode)
    return color

# Expand image
def expand(image, fill = BACKGROUND, bottom = 50, left = None, right = None, top = None):
    """
    Expands image
    
    Parameters
    ----------
    
    image: The image to expand.
    bottom, left, right, top: Border width, in pixels.
    param fill: Pixel fill value (a color value).  Default is 0 (black).
    
    return: An image.
    """
    
    
    if left == None:
        left = 0
    if right == None:
        right = 0
    if top == None:
        top = 0
        
    width = left + image.size[0] + right
    height = top + image.size[1] + bottom - 100
    out = Image.new(image.mode, (width, height), _color(fill, image.mode))
    out.paste(image, (left, top))
    return out

# Add border
def add_border(input_image, output_image, fill=BACKGROUND, bottom = 50, left = None, right = None, top = None):
    """ Adds border to image and saves it.
    Parameters
    ----------
    
        
    input_image: str,
        String object for the image you want to load. This is the name of the file you want to read.
    
    output_image: str,
        String object for the output image name. This is the name of the file you want to export.
    
    fill: str,
        Hex code for border color. Default is set to reddish. 
        
    bottom, left, right, top: int,
        Integer object specifying the border with in pixels.
    
    """
    
    
    if left == None:
        left = 0
    if right == None:
        right = 0
    if top == None:
        top = 0
        
    img = Image.open(input_image)
    bimg = expand(img, bottom = bottom, left = left, right = right, top = top, fill= fill)
    bimg.save(output_image)
    return bimg

# bbox is same format as from:
# https://boundingbox.klokantech.com
# csv RAW format
def get_map(bbox):
    # Get data for places
    G = ox.graph_from_bbox(bbox[3], bbox[1], bbox[2], bbox[0], network_type = "drive", simplify = True)
    return G

def create_colors_and_widths(color_map, G):
    edge_data = []
    for u, v, k, data in G.edges(keys=True, data=True):
        edge_data.append(data)

    roadColors = []
    for item in edge_data:
        if "length" in item.keys():

            if item["length"] <= 100:
                color = color_map['short_road']

            elif item["length"] > 100 and item["length"] <= 200:
                color = color_map['medium_road']

            elif item["length"] > 200 and item["length"] <= 400:
                color = color_map['medium_long_road']

            elif item["length"] > 400 and item["length"] <= 800:
                color = color_map['long_road']

            else:
                color = color_map['default']
        roadColors.append(color)
        
    roadWidths = []
    # TODO: use thickness map
    for item in edge_data:
        if "footway" in item["highway"] or "living_street" in item['highway'] or 'tertiary_link' in item['highway'] or item['length'] < 100:
            linewidth = 0
        else:
            linewidth = 2.5

        roadWidths.append(linewidth)
    return (roadColors, roadWidths)

def get_cemeteries(bbox, num_graveyards):
    import numpy as np
    cemeteries = ox.geometries_from_bbox(bbox[3], bbox[1], bbox[2], bbox[0], tags={'landuse': ['cemetery']})#, 'amenity': 'grave_yard'})
    cems = cemeteries[cemeteries.name != 'Cemetery']
    cems = cems[cems.name != np.nan]
    cemeteries = cems.dropna(axis=0, subset=['name'])
    
    cemeteries['area'] = cemeteries['geometry'].apply(lambda g: g.area)

    min_diff = 0
    if num_graveyards == 'SMALL':
        min_diff = 0
    elif num_graveyards == 'MEDIUM':
        cemeteries['area'].std()/2
    elif num_graveyards == 'LARGE':
        cemeteries['area'].std()

    cemetery_min_area = cemeteries['area'].mean() - min_diff

    return cemeteries[cemeteries['area'] > cemetery_min_area]

def plot_map(bbox, num_graveyards):
    G = get_map(bbox)
    roadColors, roadWidths = create_colors_and_widths(color_map, G)
    cemeteries = get_cemeteries(bbox, num_graveyards)
    
         # Make Map
    fig1, ax1 = ox.plot_graph(G, node_size=0,show=False,
                                        figsize=(40,40), dpi = 300, edge_color=roadColors,
                              bgcolor=BACKGROUND,
                              edge_linewidth=roadWidths, edge_alpha=1)
    fig1.set_facecolor(BACKGROUND)
    # plot cemeteries
    fig2, ax2 = ox.plot.plot_footprints(cemeteries, color=CEMETERY, show=False,
                                        dpi = 300,  ax=ax1,
                                        bgcolor = BACKGROUND, save = False)

    # plot cemetery labels (numbers)
    legend_elements = []
    
    # Text and marker size
    markersize = 16
    fontsize = 25

    cemetery_objs = []
    
    for n, data in enumerate(cemeteries[['name', 'geometry']].to_dict('records')):
        number_text = "{}".format(n)
        name_text = data['name']
#        c = data['geometry'].centroid
        b = data['geometry'].bounds
        c = [b[0], b[1]]

        cemetery_objs.append({
            "lat": c[0],
            "lng": c[1],
            "name": name_text,
            "id": int(number_text)})
        
        print("Placing label {} for {} at {}, {}".format(number_text, name_text, c[0], c[1]))
        ax2.annotate(number_text,(c[0], c[1]), c=BACKGROUND, fontsize=25,
                     fontfamily='monospace',
             bbox={"boxstyle" : "circle", "color":"#dfddc7", "edgecolor":BACKGROUND})
        
        # add legend marker
        
        legend_element = Line2D([0], [0], marker='${}$'.format(number_text), 
                                color="#dfddc7",
                                linestyle="None",
                                label="{}".format(name_text), markersize=30)
                               #facecolor='#dfddc7')
                               #markerfacecolor='#dfddc7')
        legend_elements.append(legend_element)


    l = ax2.legend(handles=legend_elements, bbox_to_anchor=(0, 0), loc='upper left', 
                   frameon=False, 
                   ncol=4,
                   framealpha = 1,
                  facecolor = BACKGROUND, fontsize = fontsize, prop={'family':"monospace", 'size':25})  

    # Legend font color
    for text in l.get_texts():
        text.set_color("#dfddc7")
        
    # Save figure
    fig2.set_frameon(True)
    fig1.savefig("bbox.png", dpi=300, bbox_inches='tight', format="png", facecolor=BACKGROUND, transparent=False)
    fig2.savefig("bbox_cemetery.png", dpi=300, bbox_inches='tight', format="png", facecolor=BACKGROUND, transparent=False)
    close()
    return ('bbox_cemetery.png', cemetery_objs, len(cemetery_objs))
