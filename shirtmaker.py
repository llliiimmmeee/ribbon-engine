from PIL import Image, ImageDraw, ImageFont
import glob

def getRibbons(pathToRibbons: str) -> dict[str, Image.Image]:
    """getRibbons() returns a list of all ribbons (stored as PNG files in a folder) in PIL format in a given directory.

    Args:
        pathToRibbons str: The directory path under which the ribbon images are located. They can be under subdirectories, too.

    Returns:
        list[Image.Image]: The list of ribbon images in the given directory.
    """
    ribbons: dict = {}
    for file in glob.glob(pathToRibbons + "/*.png"):
        ribbons[file] = Image.open(file)
    return ribbons

def newTShirt() -> Image.Image:
    """Creates a blank 128x128 canvas for the ribbons to go on.

    Returns:
        Image.Image: Blank 128x128 image.
    """

    return Image.new("RGBA", (128, 128), (0, 0, 0, 0))

def arrangeRibbons(ribbons: list[Image.Image], ribbonDimensions: tuple[int, int] = (9, 3), ribbonsPerRow: int = 4, outlineColorRGBA: tuple[int, int, int, int] = (80, 80, 80, 255)) -> Image.Image:
    """Arranges a given list of ribbons into the regular layout.

    Args:
        ribbons (list[Image.Image]): A list of ribbons as images.
        ribbonDimensions (tuple[int, int]): The X and Y size of the ribbons.
        ribbonsPerRow (int): The amount of ribbons to fit in each row.
        outlineColorRGBA (tuple[int, int, int, int]): The color to outline the ribbons with.

    Returns:
        Image.Image: An image containing all the ribbons organized in the regular layout.
    """

    rows: list = []
    while len(ribbons) > 0:
        rows.append( ribbons[0:min(len(ribbons), ribbonsPerRow)] )
        ribbons = ribbons[min(len(ribbons), ribbonsPerRow):]

    rowAmount = len(rows)
    resultImage: Image.Image = Image.new("RGBA", (int(1 + (ribbonDimensions[0] + 1)*ribbonsPerRow), int(rowAmount*(ribbonDimensions[1]+1) + 1)), (255, 255, 255, 0))
    for rowIndex, row in enumerate(rows):
        rowLength = len(row)
        for ribbonIndex, ribbon in enumerate(row):
            ribbonOriginX: int = int(((ribbonDimensions[0]+1)/2)*(ribbonsPerRow - len(row)) + (ribbonDimensions[0]+1)*ribbonIndex + 1)
            ribbonOriginY: int = int(rowAmount*(ribbonDimensions[1]+1) - (rowAmount-rowIndex)*(ribbonDimensions[1]+1) + 1)

            # Create a black box to place the ribbon on
            borderOriginX: int = int(ribbonOriginX - 1)
            borderOriginY: int = int(ribbonOriginY - 1)
            borderMaxX: int = int(borderOriginX + ribbonDimensions[0] + 1)
            borderMaxY: int = int(borderOriginY + ribbonDimensions[1] + 1)

            draw = ImageDraw.Draw(resultImage)
            draw.rectangle([borderOriginX, borderOriginY, borderMaxX, borderMaxY], outline = outlineColorRGBA)

            # Place the ribbon
            ribbon: Image.Image = ribbon.convert("RGBA")
            resultImage.paste(ribbon, (ribbonOriginX, ribbonOriginY, ribbonOriginX+ribbonDimensions[0], ribbonOriginY+ribbonDimensions[1]))

    return resultImage

def placeRibbonGrid(tShirt: Image.Image, ribbons: Image.Image, origin: tuple[int, int], alignTop: bool = True) -> Image.Image:
    """Places a ribbon grid (image) onto a t-shirt image at a given point.

    Args:
        tShirt (Image.Image): An RGBA to place the ribbons onto.
        ribbons (Image.Image): An image containing a grid of ribbons to place onto the t-shirt.
        origin (tuple[int, int]): The point at which to place the ribbons.
        alignTop (bool, optional): True to place the image with the origin as the top-left corner, false to place the image with the origin as the bottom-left corner. Defaults to True.

    Returns:
        Image.Image: A copy of the t-shirt with the ribbons placed.
    """

    resultImage: Image.Image = tShirt

    if resultImage.mode != "RGBA":
        print("Warning: The t-shirt provided for placeRibbonGrid() wasn't in mode 'RGBA' and may have incorrect transparency.")
        resultImage = resultImage.convert("RGBA")

    if ribbons.mode != "RGBA":
        print("Warning: The ribbon image provided for placeRibbonGrid() wasn't in mode 'RGBA' and may have incorrect transparency.")
        ribbons = ribbons.convert("RGBA")

    if not (0 <= origin[0] < tShirt.size[0]) or not (0 <= origin[1] < tShirt.size[1]):
        print("Warning: The origin was placed outside of the t-shirt. Ribbons may be partially obscured.")

    if not alignTop:
        origin = (origin[0], origin[1]-ribbons.size[1])

    resultImage.paste(ribbons, (origin[0], origin[1], origin[0] + ribbons.size[0], origin[1] + ribbons.size[1]))

    return resultImage

def makeNametape(template: Image.Image, text: str, font: ImageFont.ImageFont, color: tuple[int, int, int, int] = (255, 255, 255, 255)) -> Image.Image:
    """Generates a nametape image with given template, font, text content, and color. Warns you in console the text is too long.

    Args:
        template (Image.Image): A nameplate template to place the nameplate text on.
        text (str): The text to place on the nameplate.
        font (ImageFont.ImageFont): The font to have the text in, recommended to be in bitmap format and 5px tall.
        color (tuple[int, int, int, int], optional): The color of the text. Defaults to (255, 255, 255, 255).

    Returns:
        Image.Image: A copy of the nameplate with the text enscribed on it.
    """
    nametape: Image.Image = template

    if nametape.mode != "RGBA":
        print("Warning: nametape template for makeNametape wasn't in RGBA color mode and output was converted to RGBA.")
        resultImage = nametape.convert("RGBA")

    nametapeDraw: ImageDraw.ImageDraw = ImageDraw.Draw(nametape, "RGBA")
    textLength: int = int(nametapeDraw.textlength(text, font))

    if textLength > nametape.size[0]:
        print("Warning: The text for the nametape was longer than the template and will be cut off.")
    
    templateCenterX: int = nametape.size[0] // 2
    textCenterX: int = textLength // 2

    nametapeDraw.text((templateCenterX - textCenterX, 1), text, color, font)

    return nametape