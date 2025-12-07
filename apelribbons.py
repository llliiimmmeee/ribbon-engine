import shirtmaker
from PIL import Image as PILImage
from PIL import ImageFont, ImageTk, ImageOps
from tkinter import * # type: ignore
from tkinter import ttk, filedialog



def generateTShirtImage(ribbons: list[PILImage.Image], commendations: list[PILImage.Image], nameText: str, goldenApel: bool) -> PILImage.Image:
    """Creates a t-shirt image from the awards and name provided, in the Apel awards style.

    Args:
        ribbons (list[PILImage.Image]): The list of ribbons (as PIL images) to add to the shirt.
        commendations (list[PILImage.Image]): The list of commendations (as PIL images) to add to the shirt.
        nameText (str): The text to have on the nameplate.
        goldenApel (bool): Whether or not to place the Golden Apel award on the shirt.

    Returns:
        PILImage.Image: A t-shirt with all awards placed on it.
    """
    tShirt = shirtmaker.newTShirt()

    ribbonGrid = shirtmaker.arrangeRibbons(ribbons, ribbonsPerRow=3, outlineColorRGBA=(0, 0, 0, 255))
    commendationGrid = shirtmaker.arrangeRibbons(commendations, ribbonDimensions=(7, 2), ribbonsPerRow=3, outlineColorRGBA=(0, 0, 0, 255))
    nametapeTemplate = PILImage.open("apel/nametape.png")
    anroFont = ImageFont.load("anrofont/anrofont.pil")
    goldenApelImage = PILImage.open("apel/awards/golden.png")
    nametape = shirtmaker.makeNametape(nametapeTemplate, nameText, anroFont)

    tShirt = shirtmaker.placeRibbonGrid(tShirt, ribbonGrid, (87, 19))
    tShirt = shirtmaker.placeRibbonGrid(tShirt, commendationGrid, (89, 93))
    tShirt = shirtmaker.placeRibbonGrid(tShirt, nametape, (13, 31))

    if goldenApel:
        tShirt = shirtmaker.placeRibbonGrid(tShirt, goldenApelImage, (23, 39))

    return tShirt

root: Tk = Tk()

# prevent garbage collection
current_photo: ImageTk.PhotoImage | None = None

main_frame: ttk.Frame = ttk.Frame(root, padding=10)
main_frame.pack(padx=10, pady=10)

ribbons: dict = shirtmaker.getRibbons("apel/ribbons")
commendations: dict = shirtmaker.getRibbons("apel/commendations")

img = shirtmaker.newTShirt()
current_photo = ImageTk.PhotoImage(img)
imageLabel = Label(root, image=current_photo)
imageLabel.pack()

ribbonPanel: ttk.Frame = ttk.Frame(root, padding=10)
ribbonPanel.pack(padx=10, pady=10, side=LEFT, anchor="nw")
ttk.Label(ribbonPanel, text="Ribbons").pack(anchor="nw", side=TOP)

ribbonCheckboxStates: dict = {}
for ribbonName in ribbons.keys():
    state: BooleanVar = BooleanVar()
    checkbox: ttk.Checkbutton = ttk.Checkbutton(ribbonPanel, text=ribbonName.split("\\")[-1][:-4], variable=state)
    checkbox.pack(anchor="nw", side=TOP)
    ribbonCheckboxStates[ribbonName] = state

commendationPanel: ttk.Frame = ttk.Frame(root, padding=10)
commendationPanel.pack(padx=10, pady=10, side=LEFT, anchor="nw")
ttk.Label(commendationPanel, text="Commendations").pack(anchor="nw", side=TOP)

commendationCheckboxStates: dict = {}
for commendationName in commendations.keys():
    state: BooleanVar = BooleanVar()
    checkbox: ttk.Checkbutton = ttk.Checkbutton(commendationPanel, text=commendationName.split("\\")[-1][:-4], variable=state)
    checkbox.pack(anchor="nw", side=TOP)
    commendationCheckboxStates[commendationName] = state

nametapeEntryFrame = ttk.Frame(root, padding=10)
nametapeEntryFrame.pack(padx=10, pady=10)
ttk.Label(nametapeEntryFrame, text="Nametape text:").grid(column=0, row=0)
nametapeEntry = ttk.Entry(nametapeEntryFrame)
nametapeEntry.grid(column=1, row=0)

goldenApelState = BooleanVar()
goldenApelCheckbox = ttk.Checkbutton(root, text="Golden Apel Medal", variable=goldenApelState)
goldenApelCheckbox.pack(pady=10)

def generateButtonAction():
    """The function ran when the Generate button is clicked. Handles grabbing input, getting the ribbon image, scaling it for display, and setting global functions to store the image."""
    selectedRibbons = [a[1] for a in ribbons.items() if ribbonCheckboxStates[a[0]].get()]
    selectedCommendations = [a[1] for a in commendations.items() if commendationCheckboxStates[a[0]].get()]
    nameText = "".join(character for character in nametapeEntry.get() if character.isalpha() or character == " ").upper() # convert to only uppercase letters and spaces
    goldenApel: bool = goldenApelState.get()
    
    img = generateTShirtImage(selectedRibbons, selectedCommendations, nameText, goldenApel)
    photo = ImageOps.scale(img, 2)
    photo = ImageTk.PhotoImage(photo)
    imageLabel.configure(image=photo)
    
    # prevent garbage collection
    global current_photo
    current_photo = photo

generateButton = ttk.Button(root, text="Generate T-Shirt", command=generateButtonAction)
generateButton.pack()

def saveButtonAction():
    """The function ran when the Save button is clicked. Handles creating a file dialogue and saving the image to disk."""
    saveFilePath = filedialog.asksaveasfilename(filetypes=[("Portable Network Graphics file", "*.png"), ("All Files", "*.*")], title="Save Ribbons T-Shirt", defaultextension=".png")
    if not saveFilePath:
        return
    img.show()

saveButton = ttk.Button(root, text="Save T-Shirt", command=saveButtonAction)
saveButton.pack()

root.mainloop()