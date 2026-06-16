import shirtmaker
from PIL import Image as PILImage
from PIL import ImageFont, ImageTk, ImageOps, PngImagePlugin
from tkinter import * # type: ignore
from tkinter import ttk, filedialog, messagebox, Wm
import json
import os
import traceback

currentDir = os.path.dirname(__file__)

shirtMeta = {}

def generateTShirtImage(ribbons: list[PILImage.Image], commendations: list[PILImage.Image], awards: list[PILImage.Image], nameText: str,) -> PILImage.Image:
    """Creates a t-shirt image from the awards and name provided.

    Args:
        ribbons (list[PILImage.Image]): The list of ribbons (as PIL images) to add to the shirt.
        commendations (list[PILImage.Image]): The list of commendations (as PIL images) to add to the shirt.
        awards (list[PILImage.Image]): The list of ribbons to add to the shirt.
        nameText (str): The text to have on the nameplate.

    Returns:
        PILImage.Image: A t-shirt with all ribbons/commendations/awards placed on it.
    """
    tShirt = shirtmaker.newTShirt()

    ribbonGrid = shirtmaker.arrangeRibbons(ribbons, ribbonsPerRow=3, outlineColorRGBA=(0, 0, 0, 255))
    commendationGrid = shirtmaker.arrangeRibbons(commendations, ribbonDimensions=(7, 2), ribbonsPerRow=3, outlineColorRGBA=(0, 0, 0, 255))
    awardsGrid = shirtmaker.arrangeRibbons(awards, ribbonDimensions=(17, 17), ribbonsPerRow=2, outlineColorRGBA=(0, 0, 0, 0))
    nametapeTemplate = PILImage.open(os.path.join(currentDir, "data/nametape.png"))
    anroFont = ImageFont.load(os.path.join(currentDir, "anrofont/anrofont.pil"))
    nametape = shirtmaker.makeNametape(nametapeTemplate, nameText, anroFont)

    tShirt = shirtmaker.placeRibbonGrid(tShirt, ribbonGrid, (90, 19))
    tShirt = shirtmaker.placeRibbonGrid(tShirt, commendationGrid, (92, 73))
    tShirt = shirtmaker.placeRibbonGrid(tShirt, nametape, (7, 19))
    tShirt = shirtmaker.placeRibbonGrid(tShirt, awardsGrid, (5, 27))

    return tShirt

root: Tk = Tk()

def loadShirtFromMeta(shirt: PILImage.Image):
    """Sets all the inputs to recreate a t-shirt from its metadata, allowing it to be edited.

    Args:
        shirt (PILImage.Image): The shirt to recreate, containing metadata.
    """
    metadata = shirt.getexif()
    shirtdata = json.loads(metadata[PILImage.ExifTags.Base.ImageDescription])

    try:
        for name, state in ribbonCheckboxStates.items():
            if name in shirtdata["ribbons"]:
                state.set(True)
            else:
                state.set(False)

        for name, state in commendationCheckboxStates.items():
            if name in shirtdata["commendations"]:
                state.set(True)
            else:
                state.set(False)

        for name, state in awardCheckboxStates.items():
            if name in shirtdata["awards"]:
                state.set(True)
            else:
                state.set(False)
    except:
        print(traceback.format_exc())
        messagebox.showerror(title="Load Failure", message="Failed to load ribbons image file, file may be incompatible.")

    nametapeEntry.delete(0, END)
    nametapeEntry.insert(0, shirtdata["name-text"])

    generateButtonAction()

def loadButtonAction(event=None):
    """The function ran when the Load from Shirt button is clicked. Handles the file dialog and validation."""
    pathToShirt = filedialog.askopenfilename(filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")])
    if not pathToShirt:
        return
    shirtImage = PILImage.open(pathToShirt)
    loadShirtFromMeta(shirtImage)

def generateButtonAction(event=None):
    """The function ran when any changes to the ribbons. Handles grabbing input, getting the ribbon image, scaling it for display, and setting global functions to store the image."""
    selectedRibbons = {a[0]: a[1] for a in ribbons.items() if ribbonCheckboxStates[a[0]].get()}
    selectedCommendations = {a[0]: a[1] for a in commendations.items() if commendationCheckboxStates[a[0]].get()}
    selectedAwards = {a[0]: a[1] for a in awards.items() if awardCheckboxStates[a[0]].get()}
    nameText = "".join(character for character in nametapeEntry.get() if character.isalnum() or character == " ").upper() # convert to only uppercase letters and spaces
    
    global shirtMeta
    shirtMeta = {
        "ribbons": list(selectedRibbons.keys()),
        "commendations": list(selectedCommendations.keys()),
        "name-text": nameText,
        "awards": list(selectedAwards.keys())
    }

    # global to prevent garbage collection of image
    global img
    img = generateTShirtImage(list(selectedRibbons.values()), list(selectedCommendations.values()), nameText, list(selectedAwards.values()))
    photo = ImageOps.scale(img, 2)
    photo = ImageTk.PhotoImage(photo)
    imageLabel.configure(image=photo)
    
    # prevent garbage collection
    global current_photo
    current_photo = photo
    
def saveButtonAction(event=None):
    """The function ran when the Save button is clicked. Handles creating a file dialogue and saving the image to disk."""
    saveFilePath = filedialog.asksaveasfilename(filetypes=[("Portable Network Graphics file", "*.png"), ("All Files", "*.*")], title="Save Ribbons T-Shirt", defaultextension=".png")
    if not saveFilePath:
        return
    meta = img.getexif()
    meta[PILImage.ExifTags.Base.ImageDescription] = json.dumps(shirtMeta)
    img.save(saveFilePath, exif=meta)

# prevent garbage collection
current_photo: ImageTk.PhotoImage | None = None

main_frame: ttk.Frame = ttk.Frame(root, padding=10)
main_frame.pack(padx=10, pady=10)

ribbons: dict = shirtmaker.getRibbons(os.path.join(currentDir, "data/ribbons"))
commendations: dict = shirtmaker.getRibbons(os.path.join(currentDir, "data/commendations"))
awards: dict = shirtmaker.getRibbons(os.path.join(currentDir, "data/awards"))

img = shirtmaker.newTShirt()
current_photo = ImageTk.PhotoImage(img)
imageLabel = Label(root, image=current_photo)
imageLabel.pack()

ribbonPanel = ttk.Frame(root, padding=10)
ribbonPanel.pack(padx=10, pady=10, side=LEFT, anchor="nw")
ttk.Label(ribbonPanel, text="Ribbons").pack(anchor="nw", side=TOP)

ribbonCheckboxStates: dict = {}
for ribbonName in ribbons.keys():
    state: BooleanVar = BooleanVar()
    checkbox: ttk.Checkbutton = ttk.Checkbutton(ribbonPanel, text=ribbonName.split("\\")[-1][:-4], variable=state, command=generateButtonAction)
    checkbox.pack(anchor="nw", side=TOP)
    ribbonCheckboxStates[ribbonName] = state

commendationPanel = ttk.Frame(root, padding=10)
commendationPanel.pack(padx=10, pady=10, side=LEFT, anchor="nw")
ttk.Label(commendationPanel, text="Commendations").pack(anchor="nw", side=TOP)

commendationCheckboxStates: dict = {}
for commendationName in commendations.keys():
    state: BooleanVar = BooleanVar()
    checkbox: ttk.Checkbutton = ttk.Checkbutton(commendationPanel, text=commendationName.split("\\")[-1][:-4], variable=state, command=generateButtonAction)
    checkbox.pack(anchor="nw", side=TOP)
    commendationCheckboxStates[commendationName] = state

awardPanel = ttk.Frame(root, padding=10)
awardPanel.pack(padx=10, pady=10, side=LEFT, anchor="nw")
ttk.Label(awardPanel, text="Awards").pack(anchor="nw", side=TOP)

awardCheckboxStates: dict = {}
for awardName in awards.keys():
    state: BooleanVar = BooleanVar()
    checkbox: ttk.Checkbutton = ttk.Checkbutton(awardPanel, text=awardName.split("\\")[-1][:-4], variable=state, command=generateButtonAction)
    checkbox.pack(anchor="nw", side=TOP)
    awardCheckboxStates[awardName] = state

nametapeEntryFrame = ttk.Frame(root, padding=10)
nametapeEntryFrame.pack(padx=10, pady=10)
ttk.Label(nametapeEntryFrame, text="Nametape text:").grid(column=0, row=0)
nametapeEntry = ttk.Entry(nametapeEntryFrame)
nametapeEntry.bind("<KeyRelease>", generateButtonAction)
nametapeEntry.grid(column=1, row=0)

saveButton = ttk.Button(root, text="Save T-Shirt", command=saveButtonAction)
saveButton.pack()

loadButton = ttk.Button(root, text="Load from shirt image file", command=loadButtonAction)
loadButton.pack()

root.title("Ribbon Engine")

root.bind('<Control-s>', saveButtonAction)
root.bind('<Control-l>', loadButtonAction)

root.mainloop()
