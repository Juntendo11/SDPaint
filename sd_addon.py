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
        print("Generating image")
        filepath = scene.conf_path
        filepath = filepath + "render.png"
        ren_img = Image.open(filepath)
        gen_img = image_gen(ren_img, mytool.pos, mytool.neg)
        
        #Load stencil
        return {'FINISHED'}
    
class Render(bpy.types.Operator):
    bl_label = "Render"
    bl_idname = "render.myop_operator"

    def execute(self, context):
        scene = context.scene
        filepath = scene.conf_path
        absolute_conf_path = bpy.path.abspath(filepath)
        filepath = os.path.join(absolute_conf_path, "render.png")
        
        print(filepath)
        width,height = get_viewport_size()
        bpy.context.scene.render.resolution_x = width
        bpy.context.scene.render.resolution_y = height
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.ops.render.opengl(animation=False, render_keyed_only=False, sequencer=False, write_still=False, view_context=True)
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