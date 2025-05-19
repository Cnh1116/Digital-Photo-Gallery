import pygame
import random
import yaml
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from PIL import Image, ImageTk, ImageOps

#casino_config = r"C:\Users\cnh11\OneDrive\Desktop\Digital-Photo-Gallery\Casino-Theme\casino-theme-config.yml"
#windows95_config = r"C:\Users\cnh11\OneDrive\Desktop\Digital-Photo-Gallery\Win95-Theme\win95-theme-config.yml"
#bamboo_config = r"C:\Users\cnh11\OneDrive\Desktop\Digital-Photo-Gallery\Jungle-Theme\jungle-theme-config.yml"
#ice_config = r"C:\Users\cnh11\OneDrive\Desktop\Digital-Photo-Gallery\Ice-Theme\ice-theme-config.yml"
themes = []
themes.append(r"C:\Users\cnh11\OneDrive\Desktop\Digital-Photo-Gallery\Casino-Theme\casino-theme-config.yml")
themes.append(r"C:\Users\cnh11\OneDrive\Desktop\Digital-Photo-Gallery\Win95-Theme\win95-theme-config.yml")
themes.append(r"C:\Users\cnh11\OneDrive\Desktop\Digital-Photo-Gallery\Jungle-Theme\jungle-theme-config.yml")
themes.append(r"C:\Users\cnh11\OneDrive\Desktop\Digital-Photo-Gallery\Ice-Theme\ice-theme-config.yml")
application_config = "application-config.yml"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# HELPER FUNCTIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def Read_Theme_Config(config):
    with open(config, 'r') as theme_file:
        return yaml.safe_load(theme_file)
    
def Read_Application_Config():
    with open(application_config, 'r') as application_config_file:
        return yaml.safe_load(application_config_file)
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PHOTO GALLERY CLASS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class PhotoGallery:
    def __init__(self, gallery_window, theme_settings, application_settings):
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Base Window Set Up
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        self.gallery_window = gallery_window
        self.gallery_window.title(application_settings["Window_Title"])
        self.gallery_window.lift()
        
        self.gallery_window.focus_force()

        self.theme_settings = theme_settings
        self.application_settings = application_settings

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Directory and File
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.current_path = application_settings['Gallery_Root_Dir']
        self.root_folder = self.current_path.split("/")[-1]
        self.files = []
        self.selected_index = 0
        self.past_dirs = []

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Master Frame
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        master_bg_path = self.theme_settings["Master_Panel"]["background_image"]
        if master_bg_path and os.path.isfile(master_bg_path):
            self.master_img = Image.open(master_bg_path)
            self.master_frame = ttk.Frame(self.gallery_window)
            self.master_frame.pack(fill='both', expand=True)
            self.background_label = tk.Label(self.master_frame)
            self.background_label.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.master_frame.bind("<Configure>", self.Resize_Master_Background)


        else:
            self.master_frame = tk.Frame(self.gallery_window, 
                                        bg=self.theme_settings["Master_Panel"]["background"],
                                        bd=self.theme_settings["Master_Panel"]["bd"],
                                        highlightthickness=self.theme_settings["Master_Panel"]["highlight_thickness"],
                                        highlightcolor=self.theme_settings["Master_Panel"]["highlight_color"],
                                        highlightbackground=self.theme_settings["Master_Panel"]["highlight_background"],
                                        relief=self.theme_settings["Master_Panel"]["relief"])
            self.master_frame.pack(fill=tk.BOTH, expand=True)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Top Panel 
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.top_panel = tk.Frame(self.master_frame, 
                                        height = self.theme_settings["Top_Panel"]["height"], 
                                        bg=self.theme_settings["Top_Panel"]["background"],
                                        bd=self.theme_settings["Top_Panel"]["bd"],
                                        highlightthickness=self.theme_settings["Top_Panel"]["highlight_thickness"],
                                        highlightcolor=self.theme_settings["Top_Panel"]["highlight_color"],
                                        highlightbackground=self.theme_settings["Top_Panel"]["highlight_background"],
                                        relief=self.theme_settings["Top_Panel"]["relief"])
        
        
        top_panel_bg_path = self.theme_settings["Top_Panel"]["background_image"]
        if top_panel_bg_path and os.path.isfile(top_panel_bg_path): 
            self.top_panel.pack(side=tk.TOP, fill=tk.X, 
                                padx=self.theme_settings["Panel_Padding"], 
                                pady=(self.theme_settings["Panel_Padding"], 0))

            # Create the label that will serve as the background
            self.top_panel_bg_label = tk.Label(self.top_panel)
            self.top_panel_bg_label.place(x=0, y=0, relwidth=1, relheight=1)

            # Bind resize logic to top_panel
            self.top_panel.bind("<Configure>", self.Resize_TopPanel_Background)

        else:
            self.top_panel.pack(side=tk.TOP, 
                                fill=tk.X, 
                                padx=self.theme_settings["Panel_Padding"], 
                                pady=(self.theme_settings["Panel_Padding"],0))
            
        # Add text label to top panel to show file path
        self.file_path_label = tk.Label(self.top_panel, 
                                        text="Path: ",
                                        bg=self.theme_settings["Top_Panel"]["font"]["background_color"], 
                                        fg=self.theme_settings["Top_Panel"]["font"]["font_color"],
                                        font=(self.theme_settings["Top_Panel"]["font"]["name"], self.theme_settings["Top_Panel"]["font"]["size"]))
        self.file_path_label.place(relx=0.0, rely=0.5, anchor='w', x=10)  # Position text in the center
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Content 
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.content_panel = tk.Frame(self.master_frame, bg='brown')
        self.content_panel.pack(fill=tk.BOTH, expand=True, padx=self.theme_settings["Panel_Padding"], pady=self.theme_settings["Panel_Padding"])

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # File List Panel 
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.left_frame = tk.Frame(self.content_panel,
                                    width=theme_settings["File_List"]["width"],
                                    bg=self.theme_settings["File_List"]["background"],
                                    bd=self.theme_settings["File_List"]["bd"],
                                    highlightthickness=self.theme_settings["File_List"]["highlight_thickness"],
                                    highlightcolor=self.theme_settings["File_List"]["highlight_color"],
                                    highlightbackground=self.theme_settings["File_List"]["highlight_background"],
                                    relief=self.theme_settings["File_List"]["relief"])
        self.left_frame.pack_propagate(False)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.file_listbox = tk.Listbox(self.left_frame, activestyle="none",
                                       selectbackground=theme_settings["File_List"]["select_background"],
                                       selectforeground=theme_settings["File_List"]["select_foreground"],
                                       highlightbackground=theme_settings["File_List"]["highlight_background"],
                                       highlightcolor=theme_settings["File_List"]["highlight_color"],
                                       background=theme_settings["File_List"]["background"],
                                       foreground=theme_settings["File_List"]["foreground"],
                                       font=(theme_settings["File_List"]["font"]["name"], theme_settings["File_List"]["font"]["size"]))
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        self.file_listbox.focus_set()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Image Viewer Panel
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.right_frame = tk.Frame(self.content_panel, 
                                    bd=self.theme_settings["Image_Viewer"]["bd"], 
                                    highlightthickness=self.theme_settings["Image_Viewer"]["highlight_thickness"], 
                                    highlightbackground=theme_settings["Image_Viewer"]["highlight_background"],
                                    relief=self.theme_settings["Image_Viewer"]["relief"],
                                    highlightcolor=self.theme_settings["Image_Viewer"]["highlight_color"],
                                    background=self.theme_settings["Image_Viewer"]["background"])
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH )
        
        self.canvas=tk.Canvas(self.right_frame, bg=theme_settings["Image_Viewer"]["background"], width=1000, height=1000)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.update()
        #print('I am at line 155')
        self.canvas.bind('<Configure>', self.Resize_Image)
        

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Image Storage
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.image = None
        self.tk_image = None
        
        self.folder_image_path = self.theme_settings["Folder"]["image"]
        self.error_image_path = self.theme_settings["Error"]["image"]
        self.folder_image = self.Load_Image_Safely(self.folder_image_path)
        self.error_image = self.Load_Image_Safely(self.error_image_path)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Sound Initialization
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        pygame.mixer.init()
        self.file_select_up = None
        self.file_select_down = None
        self.enter_folder = None
        self.leave_folder = None
        self.start_up_sound = None
        self.image_error_sound = None
        self.file_select_error = None
        self.delete_file_sound = None
        self.rotate_image_sound = None
        
        if os.path.isfile(self.theme_settings["Sound"]["up_arrow"]):
            self.file_select_up = pygame.mixer.Sound(self.theme_settings["Sound"]["up_arrow"])
        if os.path.isfile(self.theme_settings["Sound"]["down_arrow"]):
            self.file_select_down = pygame.mixer.Sound(self.theme_settings["Sound"]["down_arrow"])
        if os.path.isfile(self.theme_settings["Sound"]["file_select_error"]):
            self.file_select_error = pygame.mixer.Sound(self.theme_settings["Sound"]["file_select_error"])
        if os.path.isfile(self.theme_settings["Sound"]["entering_folders"]):
            self.enter_folder = pygame.mixer.Sound(self.theme_settings["Sound"]["entering_folders"])
        if os.path.isfile(self.theme_settings["Sound"]["leaving_folders"]):
            self.leave_folder = pygame.mixer.Sound(self.theme_settings["Sound"]["leaving_folders"])
        if os.path.isfile(self.theme_settings["Sound"]["start_up_sound"]):
            self.start_up_sound = pygame.mixer.Sound(self.theme_settings["Sound"]["start_up_sound"])
        if os.path.isfile(self.theme_settings["Sound"]["image_error"]):
            self.image_error_sound = pygame.mixer.Sound(self.theme_settings["Sound"]["image_error"])
        if os.path.isfile(self.theme_settings["Sound"]["delete_file"]):
            self.delete_file_sound = pygame.mixer.Sound(self.theme_settings["Sound"]["delete_file"])
        if os.path.isfile(self.theme_settings["Sound"]["rotate_image"]):
            self.rotate_image_sound = pygame.mixer.Sound(self.theme_settings["Sound"]["rotate_image"])

        if self.file_select_up:
            self.file_select_up.set_volume(0.4)
        
        if self.file_select_down:
            self.file_select_down.set_volume(0.4)
        
        if self.file_select_error:
            self.file_select_error.set_volume(0.4)
        
        if self.enter_folder:
            self.enter_folder.set_volume(0.4)
        
        if self.leave_folder:
            self.leave_folder.set_volume(0.4)
        
        if self.start_up_sound:
            self.start_up_sound.set_volume(0.4)
        
        if self.image_error_sound:
            self.image_error_sound.set_volume(0.4)
        
        if self.delete_file_sound:
            self.delete_file_sound.set_volume(0.4)

        if self.rotate_image_sound:
            self.rotate_image_sound.set_volume(0.4)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Key bindings at root level for global focus
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.gallery_window.bind("<Up>", self.On_Arrow_Key)
        self.gallery_window.bind("<Down>", self.On_Arrow_Key)
        self.gallery_window.bind("<Left>", self.On_Arrow_Key)
        self.gallery_window.bind("<Right>", self.On_Arrow_Key)
        self.gallery_window.bind("<Escape>", self.Quit)
        self.gallery_window.bind("<F2>", self.Rename_File)
        self.gallery_window.bind("<F4>", self.Delete_File)
        self.gallery_window.bind("<r>", self.Rotate_File)
        self.gallery_window.bind("<R>", self.Rotate_File)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Get First Image
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.gallery_window.after_idle(self.Report_Canvas_Size)
        self.gallery_window.after_idle(self.On_Startup_Complete)

        if self.start_up_sound:
            self.start_up_sound.play()
        
    def Do_Nothing(self, event=None):
        return

    def Report_Canvas_Size(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        #print(f"Canvas size (after idle): {width} x {height}")


    def Resize_Master_Background(self, event):
        new_width = event.width
        new_height = event.height
        resized = self.master_img.resize((new_width, new_height), Image.BILINEAR)
        photo = ImageTk.PhotoImage(resized)
        self.background_label.config(image=photo)
        self.background_label.image = photo  # Prevent garbage collection

    def Resize_TopPanel_Background(self, event):
        img = Image.open(self.theme_settings["Top_Panel"]["background_image"])

        # Get label size
        self.gallery_window.update_idletasks()  # Ensure correct size
        label_width = self.top_panel_bg_label.winfo_width()
        label_height = self.top_panel_bg_label.winfo_height()

        if label_width < 10 or label_height < 10:
            # Fallback to default size if label hasn't fully rendered
            label_width, label_height = 400, 400

        # Resize & crop image to fill label while keeping aspect ratio
        img_fitted = ImageOps.fit(img, (label_width, label_height), method=Image.LANCZOS)

        self.photo = ImageTk.PhotoImage(img_fitted)
        self.top_panel_bg_label.configure(image=self.photo)

    def Rename_File(self, event=None):
        selected_file = self.files[self.selected_index]
        full_path = os.path.join(self.current_path, selected_file)
        file_name, file_extension = os.path.splitext(selected_file)

        new_name = simpledialog.askstring("Rename File", f"Enter new name for {file_name}:")
        if not new_name:
            return

        new_file_path = os.path.join(self.current_path, new_name + file_extension)

        try:
            os.rename(full_path, new_file_path)
            print(f"Renamed {selected_file} to {new_name + file_extension}")
            self.Update_File_List(self.current_path, direction=None, new_filename=(new_name + file_extension))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename file:\n{e}")

    def Load_Image_Safely(self, path):
        try:
            if os.path.isfile(path):
                img = Image.open(path)
                return img
        except:
            pass
        return None

    def Delete_File(self, event=None):
        selected_file = self.files[self.selected_index]
        full_path = os.path.join(self.current_path, selected_file)
        if not full_path:
            return

        confirm = messagebox.askyesno("Delete File", f"Are you sure you want to delete:\n\n{full_path}?")
        if confirm:
            try:
                os.remove(full_path)
                print(f"Deleted: {full_path}")
                next_index = min(self.selected_index, len(self.files) - 2)
                self.selected_index = max(0, next_index)
                self.Update_File_List(self.current_path)
                self.delete_file_sound.play()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete file:\n{e}")

    def Rotate_File(self, event=None):
        if not self.files:
            return
        
        selected_file = self.files[self.selected_index]
        full_path = os.path.join(self.current_path, selected_file)

        try:
            img = Image.open(full_path)
            rotated_img = img.rotate(-90, expand=True)
            rotated_img.save(full_path)  # Overwrite original; or use another filename to preserve original
            self.rotate_image_sound.play()

            self.image = rotated_img  # Store updated image
            self.Resize_Image()       # Redisplay
            print(f"Rotated and saved: {selected_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rotate image:\n{e}")

    def Update_File_List(self, path, direction=None, new_filename=None):
        self.current_path = path
        allowed_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')

        entries = os.listdir(path)
        entries.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
        
        # Filter entries: keep directories and image files
        filtered_entries = []
        for f in entries:
            full_path = os.path.join(path, f)
            if os.path.isdir(full_path) or f.lower().endswith(allowed_extensions):
                filtered_entries.append(f)
        
        self.files = filtered_entries

        self.file_listbox.delete(0, tk.END)
        for f in self.files:
            full_path = os.path.join(path, f)
            display = f + "/" + f" ({sum(1 for entry in os.listdir(full_path))})" if os.path.isdir(full_path) else f
            self.file_listbox.insert(tk.END, display)

        # Restore selection
        print(f"BEFORE:\n\tLength of files: {len(self.files)}\n\tFiles:\n\t{self.files}\n\tLength of past dir: {len(self.past_dirs)}\n\tPastDirs: {self.past_dirs}")
        if self.files:
            if direction == "Right":
                self.selected_index = 0
            if direction == "Left":
                self.selected_index = 0
                for i in range(len(self.files)):
                    #print(self.files[i])
                    for dir in self.past_dirs:
                        #print(os.path.basename(dir))
                        if self.files[i] == os.path.basename(dir):
                            print(f"Found a match: INDEX {i} {self.files[i]} == {os.path.basename(dir)}")
                            self.selected_index = i
            if new_filename:
                for i in range(len(self.files)):
                    if new_filename == self.files[i]:
                        self.selected_index = i

            
            self.file_listbox.select_set(self.selected_index)
            self.file_listbox.activate(self.selected_index)
        print(f"AFTER:\n\tLength of files: {len(self.files)}\n\tFiles:\n\t{self.files}\n\tLength of past dir: {len(self.past_dirs)}\n\tPastDirs: {self.past_dirs}\n\tFiles at Index {self.selected_index}: {self.files[self.selected_index]}")
        self.Display_Selected()
        print(f"INDEX: {self.selected_index}")
        self.file_listbox.see(self.selected_index)

        full_file_path = self.current_path.replace("\\", "/")
        folder_list = full_file_path.split("/")
        for i in range(len(folder_list)):
            if folder_list[i] == self.root_folder:
                index = i

        new_path = ""
        for i in range(index, len(folder_list)):
            new_path += f"/{folder_list[i]}"

        self.file_path_label.config(text=f"Path: {new_path}")
    
    def On_Arrow_Key(self, event):
        if not self.files:
            print("Not file, returning")
            return
        
        # Niche cases to do nothing and exit the function ~~ ~~ ~~
        if event.keysym == "Left" and self.current_path == self.application_settings["Gallery_Root_Dir"]:
            #if(not pygame.mixer.get_busy()):
            self.file_select_error.play()
            print("At gallery root dir, cannot go back.")
            return
        
        if event.keysym == "Down" and self.selected_index == len(self.files) - 1 :
            self.selected_index = 0 - 1
            self.file_listbox.see(self.selected_index)
            #if(not pygame.mixer.get_busy()):
            self.file_select_up.play()
        
        if event.keysym == "Up" and self.selected_index == 0:
            self.selected_index = len(self.files)
            #if(not pygame.mixer.get_busy()):
            self.file_select_up.play()

        # LOGIC ~~ ~~ ~~
        if event.keysym == "Down":
            self.selected_index = min(len(self.files) - 1, self.selected_index + 1)
            #if(not pygame.mixer.get_busy()):
            self.file_select_down.play()
        
        elif event.keysym == "Up":
            self.selected_index = max(0, self.selected_index - 1)
            #if(not pygame.mixer.get_busy()):
            self.file_select_up.play()
        
        elif event.keysym == "Left" and self.current_path != self.application_settings["Gallery_Root_Dir"]:
            #if(not pygame.mixer.get_busy()):
            self.leave_folder.play()
            print(f"Before Update File List: {self.past_dirs}")
            self.Update_File_List(os.path.dirname(self.current_path), "Left")
            self.past_dirs.pop()

        elif event.keysym == "Right":
            if not self.files:
                return
            self.file_listbox.xview_moveto(0.0)
            selected_file = self.files[self.selected_index]
            full_path = os.path.join(self.current_path, selected_file)
            if os.path.isdir(full_path):
                
                self.past_dirs.append(full_path.replace("\\", "/"))
                print(f"Before Update File List: {self.past_dirs}")
                self.Update_File_List(full_path, "Right")
                #if(not pygame.mixer.get_busy()):
                self.enter_folder.play()
            else:
                #if(not pygame.mixer.get_busy()):
                self.file_select_error.play()
            return    

        self.file_listbox.select_clear(0, tk.END)
        self.file_listbox.select_set(self.selected_index)
        self.file_listbox.activate(self.selected_index)
        #print("Displaying Selected")
        self.file_listbox.see(self.selected_index)
        self.Display_Selected() 

    def Display_Selected(self):
        selected_file = self.files[self.selected_index]
        full_path = os.path.join(self.current_path, selected_file)

        self.image = None
        self.tk_image = None
        self.canvas.delete("all")

        if os.path.isdir(full_path):
            self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(), fill=self.theme_settings["Error"]["background_color"])
            self.image = self.folder_image
            #print("I am a dir, Resizing Image")
            self.Resize_Image()
            return
            
        try:
            self.image = Image.open(full_path)
            self.Resize_Image()
        except Exception as e:
            print(f"Failed to open image: {e}")
            self.image_error_sound.play()
            self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(), fill=self.theme_settings["Error"]["background_color"])
            self.image = self.error_image
            self.Resize_Image()

    def On_Startup_Complete(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        #print(f"Startup Canvas Dimensions: {canvas_width} x {canvas_height}")

        # Now it's safe to load and display the first image
        self.Update_File_List(self.current_path, "Right")

    def Resize_Image(self, event=None):
        if self.image:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Avoid resizing if canvas isn't properly initialized yet
            if canvas_width < 2 or canvas_height < 2:
                print("Canvas < 2 dimensions, leaving resize_image")
                #return

            # Get original image dimensions
            img_width, img_height = self.image.size

            # Calculate aspect ratio preserving scale
            ratio = min(canvas_width / img_width, canvas_height / img_height)
            new_width = max(1, int(img_width * ratio))
            new_height = max(1, int(img_height * ratio))

            # Resize and center the image
            img_copy = self.image.copy()
            img_copy = img_copy.resize((new_width, new_height), Image.Resampling.LANCZOS)

            self.tk_image = ImageTk.PhotoImage(img_copy)
            #self.canvas.delete("all")
            #print("Creating image")
            self.canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=self.tk_image)


    def Quit(self, event=None):
        self.gallery_window.destroy()


def main():
    # Load our Theme and Application Configs
    try:
        theme_choice = int(input("Which theme to use?\n\t1. Casino\n\t2. Windows95\n\t3. Forest\n\t4. Ice\n---> "))
        theme_index = theme_choice - 1
    
        theme = themes[theme_index]
    except Exception as e:
        print("Invalid theme choice, picking a random one ...")
        theme = themes[random.randrange(0, len(themes)) - 1]

    
    theme_settings = Read_Theme_Config(theme)
    application_settings = Read_Application_Config()

    # Create our GUI Window
    gallery_window = tk.Tk()
    gallery_window.attributes('-fullscreen', True)
    photo_galery_object = PhotoGallery(gallery_window, theme_settings, application_settings)

    # Run the Gallery Window Loop
    photo_galery_object.gallery_window.mainloop()
    

if __name__ == "__main__":
    main()