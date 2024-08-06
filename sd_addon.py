import bpy
import os 
from PIL import Image

from sdpaint.sd.img2img import image_gen
from sdpaint.bpy.viewport import get_viewport_size

from bpy.props import (StringProperty,
                       PointerProperty,
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
        absolute_conf_path = bpy.path.abspath(scene.conf_path)
        filepath = os.path.join(absolute_conf_path, "render.png")
        outPath  = os.path.join(absolute_conf_path, "gen.png")
        print("Generating image")
        ren_img = Image.open(filepath)
        gen_img = image_gen(absolute_conf_path,ren_img, mytool.pos, mytool.neg)    #output path, img, prompt, negative
        set_tex(context, absolute_conf_path,outPath)
        #Load stencil
        return {'FINISHED'}
    
class Render(bpy.types.Operator):
    bl_label = "Render"
    bl_idname = "render.myop_operator"

    def execute(self, context):
        scene = context.scene
        absolute_conf_path = bpy.path.abspath(scene.conf_path)
        filepath = os.path.join(absolute_conf_path, "render.png")
        
        width,height = get_viewport_size()
        bpy.context.scene.render.resolution_x = width
        bpy.context.scene.render.resolution_y = height
        bpy.context.scene.render.image_settings.file_format = "PNG"
        
        
        bpy.context.space_data.overlay.show_overlays = False
        bpy.ops.render.opengl(animation=False, render_keyed_only=False, sequencer=False, write_still=False, view_context=True)
        bpy.context.space_data.overlay.show_overlays = True
        
        bpy.data.images["Render Result"].save_render(filepath)
        print("Rendering image")
        return {'FINISHED'}
    

    
# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class MyProperties(PropertyGroup):

    api: StringProperty(
        name="API Key",
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


# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class OBJECT_PT_CustomPanel(Panel):
    bl_label = "SD_Paint"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Tools"
    bl_context = "objectmode"   

    
    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        layout.prop(mytool, "api")
        layout.prop(mytool, "pos")
        layout.prop(mytool, "neg")
        
        layout.separator()
        
        col = layout.column()
        col.prop(context.scene, 'conf_path')

        layout.separator()
        
        layout.operator("generate.myop_operator")
        layout.operator("render.myop_operator")
        
        
# ------------------------------------------------------------------------
#    Functions
# ------------------------------------------------------------------------

def set_tex(context, out_path, img_path):
    """
    #bpy.context.space_data.context = 'TEXTURE'
    #bpy.ops.brush.add()
    bpy.ops.texture.new()
    bpy.ops.image.open(filepath=img_path,
                        directory=out_path,
                        files=[{"name":"render.png", "name":"render.png"}], 
                        show_multiview=False)
                        
    """
    # Path to your stencil texture image
    image_path = img_path

    # Load the image into Blender
    image = bpy.data.images.load(image_path)
                        
    # Create a new texture and assign the image to it
    texture = bpy.data.textures.new(name="StencilTexture", type='IMAGE')
    texture.image = image

    # Get the active brush
    brush = bpy.data.brushes["Draw"]

    # Create a new texture slot for the brush if it doesn't have one
    if not brush.texture_slot:
        brush.texture_slot_add()

    # Assign the texture to the brush's texture slot
    brush.texture = texture

    # Set the brush to use the texture as a stencil
    brush.texture_overlay_alpha = 1  # Overlay opacity

    print("Stencil texture applied to the brush successfully.")
    

def center_stencil():
    v3d_list = [area for area in bpy.context.screen.areas if area.type == 'VIEW_3D']
    if v3d_list:
    mainV3D = max(v3d_list, key=lambda area: area.width * area.height)
       
    x = mainV3D.width / 2
    y = mainV3D.height / 2
    
    try:
        if bpy.context.sculpt_object:   
            brushName = bpy.context.tool_settings.sculpt.brush.name
        else:
            brushName = bpy.context.tool_settings.image_paint.brush.name
            
        bpy.data.brushes[brushName].stencil_pos.xy = x, y
    except:
        pass


# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    MyProperties,
    OBJECT_PT_CustomPanel,
    Generate,
    Render,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)
    
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