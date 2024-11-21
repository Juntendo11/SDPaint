# ------------------------------------------------------------------------
#   Blender stencil painter
#   Powered by Stable Diffusion and Automatic1111 webui api
#   2024/11/16
#   To do 
#   -Fix stencil opacity
#   -Add image preview panel
#   -Segmentation to blend/mask areas  (2 channel paint)?
# ------------------------------------------------------------------------

import bpy
import os 
import numpy as np
from PIL import Image
from math import *
from mathutils import *

from sdpaint.sd.img2img import image_gen, generate_seed
from sdpaint.bpy.viewport import get_viewport_size, get_viewport_matrix, restore_viewport
from sdpaint.img.img_process import crop_image, div_image_size


from bpy.props import (StringProperty,
                       PointerProperty,
                       IntProperty,
                       )

from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       AddonPreferences,
                       )
# ------------------------------------------------------------------------
#    Info
# ------------------------------------------------------------------------                       
bl_info = {
    "name": "SDPaint",
    "blender": (3, 30, 0),
    "category": "Object",
}
# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------
    
class Generate(bpy.types.Operator):
    bl_label = "Generate"
    bl_idname = "generate.myop_operator"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        my_props = scene.my_props
        temp_props = scene.temp_props
        
        #SD API
        prompt = mytool.lora + mytool.pos
        negative = mytool.neg
        seed_val = my_props.seed    #default = -1 (random)
        
        # Store used seed if randomized
        if seed_val == -1:
            seed_val = generate_seed()
            #Store seed to temp
            temp_props.temp_seed = seed_val
            
        cfg_scale = my_props.cfg
        step_val = my_props.steps
        denoise_val = my_props.denoise
        
        #Path
        absolute_conf_path = bpy.path.abspath(scene.conf_path)
        filepath = os.path.join(absolute_conf_path, "render.png")
        outPath  = os.path.join(absolute_conf_path, "gen.png")
        print("Generating image")
        
        ren_img = Image.open(filepath)
        #Crop rendered image to size divisible by 8 (lower ceil)
        crop_img = crop_image(ren_img)
        gen_img = image_gen(absolute_conf_path,
                            crop_img,prompt,
                            negative,seed_val,
                            step_val,
                            cfg_scale,
                            denoise_val)    #output path, img, prompt, negative
                            
        #Load stencil
        import_brush(context, outPath)
        return {'FINISHED'}
    
class Render(bpy.types.Operator):
    bl_label = "Render"
    bl_idname = "render.myop_operator"

    def execute(self, context):
        scene = context.scene
        temp_props = scene.temp_props
        
        #Output Path
        absolute_conf_path = bpy.path.abspath(scene.conf_path)
        filepath = os.path.join(absolute_conf_path, "render.png")
        
        #Save current viewport view 
        view_matrix, perspective_matrix = get_viewport_matrix()
        
        print(view_matrix)
        print(perspective_matrix)
        temp_props.view_matrix = view_matrix
        temp_props.perspective_matrix = perspective_matrix
        
        #Render current viewport
        width,height = get_viewport_size()
        bpy.context.scene.render.resolution_x = width
        bpy.context.scene.render.resolution_y = height
        bpy.context.scene.render.image_settings.file_format = "PNG"
        
        # OpenGL viewport render settings
        # Momentary turn off UI overlays
        
        bpy.context.space_data.overlay.show_overlays = False
        bpy.ops.render.opengl(animation=False, render_keyed_only=False, 
                              sequencer=False, write_still=False, view_context=True)
                              
        bpy.context.space_data.overlay.show_overlays = True
        
        bpy.data.images["Render Result"].save_render(filepath)
        print("Rendering image")
        return {'FINISHED'}


class ReuseSeed(bpy.types.Operator):
    bl_label = "ReuseSeed"
    bl_idname = "reuseseed.myop_operator"
 
    def execute(self, context):
        scene = context.scene
        my_props = scene.my_props
        temp_props = scene.temp_props
        try:
            my_props.seed = temp_props.temp_seed
        except:
            print("Previous seed undefined!")
        return {"FINISHED"}


class CenterStencil(bpy.types.Operator):
    #Center stencil to viewport
    
    #1) Get current viewport size
    #2) Get AI image size => using div_image_size
    #3) Get center point
    #4) Get stencil dimension
    
    bl_label = "Center"
    bl_idname = "center.myop_operator"
    
    def execute(self, context):
        scene = context.scene
        
        #1
        viewport_width, viewport_height = get_viewport_size()
        
        #2 
        stencil_width, stencil_height = div_image_size(viewport_width, viewport_height)
        
        #3 Center point
        try:
            #Try incase brush may not be selected!
            brushName = bpy.context.tool_settings.image_paint.brush.name
            bpy.data.brushes[brushName].stencil_pos.xy = viewport_width/2, viewport_height/2
            bpy.data.brushes[brushName].stencil_dimension.xy = stencil_width/2, stencil_height/2

        except:
            print("No stencil brush selected")
            pass
        return {'FINISHED'}

class ClearStencil(bpy.types.Operator):
    """
    Clear All stencil textures
    #Need warning
    """
    bl_label = "Clear"
    bl_idname = "clear.myop_operator"
    
    def execute(self, context):
        scene = context.scene
        my_props = scene.my_props
        print("Pressed")
        
        # iterate over all images in the file
        """
        for img in bpy.data.images:
            img.user_clear()
        """
        try:
            mat = bpy.context.object.data.materials['Material']
            ts = mat.texture_slots[0] # first texture slot
            if ts is not None:
                ts.texture = None
        except:
            print("Texture not found")
            
        return {'FINISHED'}
    
class RestoreViewport(bpy.types.Operator):
    bl_label = "Restore"
    bl_idname = "restore.myop_operator"
    def execute(self, context):
        scene = context.scene
        my_props = scene.my_props
        temp_props = scene.temp_props
        
        viewport_matrix = temp_props.view_matrix
        perspective_matrix = temp_props.perspective_matrix
        print(type(viewport_matrix))
        
        #Pack back into 2D matrix
        viewport_matrix_packed = np.array(viewport_matrix).reshape(4,4)
        perspective_matrix_packed = np.array(perspective_matrix).reshape(4,4)
        restore_viewport(viewport_matrix_packed,perspective_matrix_packed)
        return {'FINISHED'}
    
class StencilOpacity(bpy.types.Operator):
    """
    Set stencil opacity from slider value
    """
    bl_label = "Opacity"
    bl_idname = "opacity.myop_operator"

    def execute(self, context):
        scene = context.scene
        my_props = scene.my_props
        opacity_val=my_props.opacity
        setting = self.setting
        print(opacity_val)
        
        #Get brush
        brush = bpy.context.tool_settings.image_paint.brush
        brush = bpy.data.brushes[brush_name]

        #Should change Cursor->Texture opacity
        #brush.texture_slot.opacity = opacity_val
        brush.texture_overlay_alpha = opacity_val
        #bpy.data.brushes["TexDraw"].texture_overlay_alpha = opacity_val

# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------
class TempProps(bpy.types.PropertyGroup):
    """
    Store temporary data to be used within
    """
    temp_seed: IntProperty (
        name="Temporary Seed",
        description="Temporary seed value to be reused",
        default=-1
    )
    view_matrix: bpy.props.FloatVectorProperty(
        name="View Matrix",
        size=16,  # 4x4 matrix flattened
        subtype='MATRIX',
        description="View Matrix of the 3D viewport"
    )
    perspective_matrix: bpy.props.FloatVectorProperty(
        name="Perspective Matrix",
        size=16,  # 4x4 matrix flattened
        subtype='MATRIX',
        description="Perspective Matrix of the 3D viewport"
    )

        
class MyProperties(PropertyGroup):
    
    api: StringProperty(
        name="API Key",
        description=":",
        default="",
        maxlen=1024,
        )
    lora: StringProperty(
        name="Lora",
        description=":",
        default="",
        maxlen=1024,
        )
    pos: StringProperty(
        name="Prompt",
        description=":",
        default="",
        maxlen=1024,
        )
    neg: StringProperty(
        name="Negative",
        description=":",
        default="",
        maxlen=1024,
        )
    seed: bpy.props.IntProperty(
        name="seed",
        description="Seed value",
        default=-1,
    )
    steps: bpy.props.IntProperty(
        name="steps",
        description="Sample steps",
        default=30,
        min=0,
        max=100
    )
    cfg: bpy.props.FloatProperty(
        name="cfg",
        description="cfg scale",
        default=7.0,
        min=0.0,
        max=100.0
    )
    denoise: bpy.props.FloatProperty(
        name="denoise",
        description="Denoising scale",
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    opacity: bpy.props.FloatProperty(
        name="opacity",
        description="Stencil opacity",
        default=0.5,
        min=0.0,
        max=1.0
    )

# ------------------------------------------------------------------------
#    Panel in TexPaint Mode
# ------------------------------------------------------------------------
class OBJECT_PT_CustomPanel(Panel):
    bl_label = "SD_Paint"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "SDPaint"
    bl_context = "imagepaint"
    
    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        my_props = scene.my_props
        
        #SD Paramter
        layout.prop(mytool, "api")
        layout.prop(mytool, "lora")
        layout.prop(mytool, "pos")
        layout.prop(mytool, "neg")
        layout.prop(my_props,"seed")
        layout.prop(my_props,"steps")
        layout.prop(my_props,"cfg")
        layout.prop(my_props,"denoise")

        layout.separator()
        
        #Image preview
        layout.label(text="Image Preview")
        absolute_conf_path = bpy.path.abspath(scene.conf_path)
        filepath = os.path.join(absolute_conf_path, "gen.png")

        layout.separator()
        
        #Output path
        col = layout.column()
        col.prop(context.scene, 'conf_path')

        layout.separator()

        #Buttons
        layout.operator("reuseseed.myop_operator")
        layout.operator("render.myop_operator")
        layout.operator("generate.myop_operator")
        layout.operator("clear.myop_operator")
        layout.operator("center.myop_operator")
        layout.operator("restore.myop_operator")
        #Slider
        layout.prop(my_props, "opacity")

# ------------------------------------------------------------------------
#    Functions
# ------------------------------------------------------------------------
def import_brush(context, filepath):
    file = os.path.split(filepath)[-1]

    if os.path.isfile(filepath):
        brush = bpy.data.brushes.new(file,mode='TEXTURE_PAINT')
        tex   = bpy.data.textures.new(file,type="IMAGE")
        image = bpy.data.images.load(filepath, check_existing=False)
        tex.image = image

        #Set as texture 
        brush.texture = tex
        brush.texture_slot.map_mode = 'STENCIL'

    return {'FINISHED'}

    
# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------
classes = (
    TempProps,
    MyProperties,
    OBJECT_PT_CustomPanel,
    ReuseSeed,
    Render,
    Generate,
    CenterStencil,
    ClearStencil,
    RestoreViewport,
    StencilOpacity,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)
    bpy.types.Scene.my_props = bpy.props.PointerProperty(type=MyProperties)
    bpy.types.Scene.temp_props  = bpy.props.PointerProperty(type=TempProps)

    #Directory path
    bpy.types.Scene.conf_path = bpy.props.StringProperty \
      (
      name = "Output Path",
      default = "",
      description = "Define the root path of the project",
      subtype = 'DIR_PATH',
      )

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.my_tool
    del bpy.types.Scene.conf_path

if __name__ == "__main__":
    register()